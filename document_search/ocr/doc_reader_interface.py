import io
from typing import Protocol

from document_search.entities import ProcessedDocument


class IDocumentReader(Protocol):

    def read(
        self,
        file: io.IOBase | str,
        filename: str | None = None
    ) -> tuple[ProcessedDocument, list[Exception]]: ...
