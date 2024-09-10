from typing import Literal, Protocol

DocumentStatus = Literal["Initial", "Processing", "Added", "NotFound"]


class DocumentStatusStorage(Protocol):

    async def get_status(self, document_id: str) -> DocumentStatus: ...

    async def set_status(self, document_id: str, status: DocumentStatus) -> None: ...


class LocalDocumentStatusStorage(DocumentStatusStorage):
    def __init__(self) -> None:
        self._statuses: dict[str, DocumentStatus] = {}

    async def get_status(self, document_id: str) -> DocumentStatus:
        return self._statuses.get(document_id, "NotFound")

    async def set_status(self, document_id: str, status: DocumentStatus) -> None:
        self._statuses[document_id] = status
