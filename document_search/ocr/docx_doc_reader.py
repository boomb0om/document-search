import io

from PIL import Image

from document_search.entities import ProcessedDocument
from document_search.types import DocumentFormat

from .doc_reader_interface import IDocumentReader


class DocxDocumentReader(IDocumentReader):

    def read(
        self,
        file: io.IOBase | str,
        filename: str | None = None
    ) -> tuple[ProcessedDocument, list[Exception]]:
        raise NotImplementedError()

    def extract_page_as_image(
        self,
        file: io.IOBase | str,
        file_format: DocumentFormat,
        page: int,
    ) -> Image.Image:
        raise NotImplementedError()
