from typing import Protocol

from document_search import DocEntity, VectorizedDocument


class DocumentStorage(Protocol):

    def _add_entity(self, entity: DocEntity) -> None: ...

    def add_document(self, document: VectorizedDocument) -> None: ...

    def get_relevant_indexes(
        self,
        document: VectorizedDocument,
        k: int
    ) -> list[DocEntity]: ...
