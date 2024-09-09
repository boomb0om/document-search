import uuid
from collections.abc import Iterable
from typing import Any

import faiss  # type: ignore
from langchain_community.docstore import InMemoryDocstore
from langchain_community.vectorstores.faiss import FAISS
from langchain_core.documents import Document
from tqdm import tqdm

from document_search.entities import DocEntity, TextDocEntity, TextDocument, EntityPosition
from document_search.search.embedders import TextEntityEmbedderE5
from document_search.storages.interfaces import DocumentStorage


def split_to_batches(lst: list[Any], n: int) -> Iterable[list[Any]]:
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


class DocumentStorageE5(DocumentStorage):
    def __init__(self, embedder: TextEntityEmbedderE5, batch_size: int = 16) -> None:
        self.embedder = embedder
        self.batch_size = batch_size
        self.index = faiss.IndexFlatIP(self.embedder.embed_shape)

        self.vector_store = FAISS(
            embedding_function=self.embedder.embedder,
            index=self.index,
            docstore=InMemoryDocstore(),
            index_to_docstore_id={}
        )
        self.documents = {}

    def _add_text_entities_batch(self, entities: list[TextDocEntity]) -> None:
        documents = []
        ids = []
        for entity in entities:
            document = Document(
                page_content=entity.text,
                metadata={"position": entity.position}
            )
            doc_id = str(uuid.uuid4().hex)
            documents.append(document)
            ids.append(doc_id)
        self.vector_store.add_documents(documents, ids=ids)

    def add_document(self, document: TextDocument, pbar: bool = False) -> None:
        text_entities = [i for i in document.entities if isinstance(i, TextDocEntity)]
        self.documents[document.name] = text_entities
        for batch in tqdm(split_to_batches(text_entities, self.batch_size), disable=not pbar,
                          total=len(text_entities) // self.batch_size):
            self._add_text_entities_batch(batch)

    def get_relevant_entities(self, query: str, k: int, context_length: int = 1) -> list[DocEntity]:
        results = self.vector_store.similarity_search_with_score(query, k=k)

        relevant_entities = []
        for result, _ in results:
            position = result.metadata["position"]
            text = result.page_content
            context = self.retrieve_context(position, context_length)
            relevant_entities.append(TextDocEntity(position=position, text=text, context=context))

        return relevant_entities

    def retrieve_context(self, position: EntityPosition, context_length: int = 2) -> str:
        doc_entities = self.documents.get(position.document_name, [])
        relevant_entities = []

        for entity in doc_entities:
            if position.page_number - context_length <= entity.position.page_number <= position.page_number + context_length:
                relevant_entities.append(entity.text)

        context = "\n".join(relevant_entities)
        return context