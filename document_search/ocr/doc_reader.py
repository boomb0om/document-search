import io
import os

from PIL import Image

from document_search.entities import ProcessedDocument
from document_search.types import DocumentFormat

from .doc_reader_interface import IDocumentReader
from .docx_doc_reader import DocxDocumentReader
from .pdf_doc_reader import PDFDocumentReader


class DocumentReader(IDocumentReader):
    def __init__(self) -> None:
        self.docx_reader = DocxDocumentReader()
        self.pdf_reader = PDFDocumentReader()
        self.format2reader: dict[DocumentFormat, IDocumentReader] = {
            "pdf": self.pdf_reader,
            # 'docx': self.docx_reader,  # TODO
            # 'txt': TxtDocumentReader(),  # TODO
            # 'markdown': MarkdownDocumentReader(),  # TODO
        }

    def read(
        self,
        file: io.IOBase | str,
        filename: str | None = None,
        document_id: str | None = None,
    ) -> tuple[ProcessedDocument, list[Exception]]:
        if isinstance(file, str):
            file_obj = open(file, "rb")
            filename = filename if filename else os.path.basename(file)
        else:
            assert (
                filename is not None
            ), "param filename should be specified if file is a file object"
            file_obj = file  # type: ignore

        ext = filename.split(".")[-1].lower()
        if ext not in self.format2reader:
            raise ValueError(f"Unsupported file format: {ext}")

        document, errors = self.format2reader[ext].read(file_obj, filename)  # type: ignore
        for entity in document.entities:
            entity.position.document_id = document_id
        return document, errors

    def extract_page_as_image(
        self, file: io.IOBase | str, file_format: DocumentFormat, page: int
    ) -> Image.Image:
        if file_format not in self.format2reader:
            raise ValueError(f"Unsupported file format: {file_format}")

        return self.format2reader[file_format].extract_page_as_image(
            file, file_format, page
        )
