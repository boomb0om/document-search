from typing import Protocol

from document_search import DocEntity
from document_search.entities import TextDocument


class DocumentStorage(Protocol):

    def _add_entity(self, entity: DocEntity) -> None: ...

    def add_document(self, document: TextDocument) -> None: ...

    def get_relevant_entities(
        self,
        query: str,
        k: int
    ) -> list[DocEntity]: ...
