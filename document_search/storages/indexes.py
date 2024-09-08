import faiss  # type: ignore
from langchain_community.docstore import InMemoryDocstore  # type: ignore
from langchain_community.vectorstores.faiss import FAISS  # type: ignore
from langchain_core.documents import Document  # type: ignore

from document_search.entities import (
    DocEntity,
    TextDocEntity,
    TextDocument,
)
from document_search.search.embedders import TextEntityEmbedderE5
from document_search.storages.interfaces import DocumentStorage


class DocumentStorageE5(DocumentStorage):
    def __init__(self, embedder: TextEntityEmbedderE5) -> None:
        self.embedder = embedder
        self.index = faiss.IndexFlatL2(self.embedder.embed_shape)
        self.document_counter = 0

        self.vector_store = FAISS(
            embedding_function=self.embedder.embedder,
            index=self.index,
            docstore=InMemoryDocstore(),
            index_to_docstore_id={}
        )

    def _add_entity(self, entity: DocEntity) -> None:
        if isinstance(entity, TextDocEntity):
            document = Document(page_content=entity.text,
                                metadata={"position": entity.position})
            doc_id = f"{self.document_counter}"
            self.document_counter += 1
            self.vector_store.add_documents([document], ids=[doc_id])
        else:
            raise NotImplementedError

    def add_document(self, document: TextDocument) -> None:
        for entity in document.entities:
            self._add_entity(entity)

    def get_relevant_entities(self, query: str, k: int) -> list[DocEntity]:
        results = self.vector_store.similarity_search_with_score(query, k=k)

        return [TextDocEntity(position=result.metadata["position"],
                              text=result.page_content) for result, _ in results]
