import asyncio
import os
import uuid
import io
from contextlib import asynccontextmanager
from datetime import datetime
from dotenv import load_dotenv
import uvicorn
from starlette.concurrency import run_in_threadpool

from fastapi import FastAPI, Response, UploadFile, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from loguru import logger
import argparse

from document_search.ocr import DocumentReader, EntityProcessor
from document_search.storages import DocumentStorageE5, DocumentStorage
from document_search.search import TextEntityEmbedderE5, TextEntityEmbedder
from document_search.app import DocumentStatusStorage, LocalDocumentStatusStorage
from document_search.rag import YandexGPTRetriever
from document_search.utils import extract_image_from_file
from document_search.app.models import (
    StorageInfoResponse, StorageItemResponse, 
    SearchQuery, SearchResponse, SearchResultItem,
    GetImageData
)


storage: DocumentStorage = None
embedder: TextEntityEmbedder = None
retriever: YandexGPTRetriever = None
doc_reader: DocumentReader = DocumentReader()
status_storage: DocumentStatusStorage = LocalDocumentStatusStorage()


@asynccontextmanager
async def lifespan(app: FastAPI):
    global embedder, storage, retriever
    embedder = TextEntityEmbedderE5()
    storage = DocumentStorageE5(embedder)
    retriever = YandexGPTRetriever(embedder, storage)
    yield


app = FastAPI(lifespan=lifespan)


def process_and_add_document(doc_bytes: io.BytesIO, filename: str, doc_id: str) -> None:
    logger.info(f"Processing document {filename} with ID {doc_id}")
    
    processed_doc, errors = doc_reader.read(doc_bytes, filename=filename, document_id=doc_id)
    logger.info(f"Document {filename} processed with {len(errors)} errors")
    processed_doc.entities = EntityProcessor.merge_text_entities(processed_doc.entities)
    processed_doc.entities = EntityProcessor.filter_short_entities(processed_doc.entities)

    logger.info(f"Adding document {filename} to storage with total entities: {len(processed_doc.entities)}")
    storage.add_document(processed_doc, doc_bytes, doc_id)
    logger.info(f"Document {filename} added to storage")


async def process_and_add_document_wrap(
    doc_bytes: io.BytesIO, filename: str, doc_id: str
) -> None:
    await status_storage.set_status(doc_id, "Processing")
    await run_in_threadpool(process_and_add_document, doc_bytes, filename, doc_id)
    await status_storage.set_status(doc_id, "Added")


@app.put("/documents/add/")
async def add_document(file: UploadFile, background_tasks: BackgroundTasks):
    filename = file.filename
    doc_id = str(uuid.uuid4().hex)
    doc_bytes = io.BytesIO(file.file.read())

    await status_storage.set_status(doc_id, "Initial")

    background_tasks.add_task(
        process_and_add_document_wrap, 
        doc_bytes=doc_bytes,
        filename=filename, 
        doc_id=doc_id
    )

    return {
        'documentID': doc_id
    }


@app.get("/documents/status/")
async def get_upload_status(documentID: str):
    return {
        'status': await status_storage.get_status(documentID)
    }


@app.get("/documents/storage_info/")
async def get_storage_info() -> StorageInfoResponse:
    total_documents = len(storage.document_store)
    items = [
        StorageItemResponse(document_id=doc_id, document_filename=document.name, num_pages=document.num_pages)
        for doc_id, document in storage.document_store.items()
    ]

    return StorageInfoResponse(items=items, total_documents=total_documents)


@app.get(
    "/documents/get_image/",
    responses = {
        200: {"content": {"image/png": {}}}
    },
    response_class=Response
)
async def get_image(data: GetImageData) -> Response:
    document_format = storage.document_store[data.document_id].original_format
    document_bytes = storage.raw_store[data.document_id]
    image = await run_in_threadpool(
        extract_image_from_file, document_bytes, document_format, data.page
    )
    image_bytes = io.BytesIO()
    image.save(image_bytes, format="JPEG")
    image_bytes.seek(0)
    return Response(content=image_bytes.read(), media_type="image/png")


@app.post("/search/query/")
async def search_query(data: SearchQuery) -> SearchResponse:
    if data.use_rag:
        search_result, llm_answer = await run_in_threadpool(
            retriever.retrieve_answer_detailed, 
            data.query, k=data.top_k, context_length=data.context_length
        )
    else:
        search_result = storage.get_relevant_entities(data.query, data.top_k)
        llm_answer = None

    items = [
        SearchResultItem(
            document_id=entity.position.document_id, 
            page=entity.position.page_number, 
            text=entity.text, 
            relevance_score=score
        ) 
        for entity, score in search_result
    ]
    return SearchResponse(query=data.query, results=items, llm_answer=llm_answer)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='WebServer for document search')
    parser.add_argument('--port', type=int, help='port to use')
    args = parser.parse_args()

    uvicorn.run("main:app", host="0.0.0.0", port=args.port, reload=False)
