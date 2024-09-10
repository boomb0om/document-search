import io
from typing import Protocol
from PIL import Image

from document_search.entities import ProcessedDocument
from document_search.types import DocumentFormat


class IDocumentReader(Protocol):

    def read(
        self,
        file: io.IOBase | str,
        filename: str | None = None
    ) -> tuple[ProcessedDocument, list[Exception]]: ...

    def extract_page_as_image(
        self,
        file: io.IOBase | str,
        file_format: DocumentFormat,
        page: int,
    ) -> Image.Image: ...
