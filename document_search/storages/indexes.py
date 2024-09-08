import uuid
from collections.abc import Iterable
from typing import Any

import faiss  # type: ignore
from langchain_community.docstore import InMemoryDocstore
from langchain_community.vectorstores.faiss import FAISS
from langchain_core.documents import Document
from tqdm import tqdm

from document_search.entities import DocEntity, TextDocEntity, TextDocument
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

        for batch in tqdm(split_to_batches(text_entities, self.batch_size), disable=not pbar, total=len(text_entities) // self.batch_size):
            self._add_text_entities_batch(batch)

    def get_relevant_entities(self, query: str, k: int) -> list[DocEntity]:
        results = self.vector_store.similarity_search_with_score(query, k=k)

        return [TextDocEntity(position=result.metadata["position"],
                              text=result.page_content) for result, _ in results]
