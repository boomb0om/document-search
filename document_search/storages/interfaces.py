import io
from typing import Protocol, Optional

from document_search import DocEntity
from document_search.entities import ProcessedDocument


class DocumentStorage(Protocol):

    def _add_entity(self, entity: DocEntity) -> None: ...

    def add_document(
        self,
        document: ProcessedDocument,
        doc_bytes: io.BytesIO,
        doc_id: str | None = None,
        pbar: bool = False
    ) -> str: ...

    def get_relevant_entities(
        self,
        query: str,
        k: int,
        document_ids: Optional[list[str]] = None
    ) -> list[tuple[DocEntity, float]]: ...
