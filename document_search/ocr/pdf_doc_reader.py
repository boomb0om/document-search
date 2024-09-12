import io
import uuid
from pathlib import Path

import fitz
import pdfplumber
import PyPDF2
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTFigure, LTTextContainer
from PIL import Image

from document_search import (
    DocEntity,
    EntityPosition,
    ImageDocEntity,
    ProcessedDocument,
    TableDocEntity,
    TextDocEntity,
)
from document_search.types import DocumentFormat

from .doc_reader_interface import IDocumentReader
from .exceptions import ExtractImageError, ExtractTablesError, ExtractTextBlockError


class PDFDocumentReader(IDocumentReader):

    def convert_pdf_to_images(self, pdf_path: str) -> list[Image.Image]:
        with fitz.open(pdf_path) as pdf_document:

            def get_image(page_number: int) -> Image.Image:
                page = pdf_document.load_page(page_number)
                pix = page.get_pixmap()
                return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)

            return list(map(get_image, range(len(pdf_document))))

    def extract_page_as_image(
        self,
        file: io.IOBase | str,
        file_format: DocumentFormat,
        page: int,
    ) -> Image.Image:
        tmp_filename = str(uuid.uuid4().hex) + '.pdf'
        with open(tmp_filename, "wb") as tmpfile:
            file.seek(0)  # type: ignore
            tmpfile.write(file.read())  # type: ignore
        with fitz.open(tmp_filename) as pdf_document:
            page = pdf_document.load_page(page)
            pix = page.get_pixmap()  # type: ignore
            image = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        Path(tmp_filename).unlink(missing_ok=True)
        return image

    def _crop_image_from_pdf(
        self, element: LTFigure, page_object: PyPDF2.PageObject
    ) -> Image.Image:
        page_object.mediabox.lower_left = [element.x0, element.y0]
        page_object.mediabox.upper_right = [element.x1, element.y1]

        pdf_writer = PyPDF2.PdfWriter()
        pdf_writer.add_page(page_object)

        tmp_pdf_path = str(uuid.uuid4().hex) + '.pdf'
        try:
            with open(tmp_pdf_path, "wb") as file:
                pdf_writer.write(file)

            image = self.convert_pdf_to_images(tmp_pdf_path)[0]
        finally:
            Path(tmp_pdf_path).unlink(missing_ok=True)

        return image

    def _process_table(self, table: list[list[str | None]]) -> list[list[str]]:
        def replace_none(elem: str | None) -> str:
            return elem if elem is not None else ""

        return [
            [replace_none(table[i][j]) for j in range(len(table[0]))]
            for i in range(len(table))
        ]

    def _extract_tables(
        self,
        table_parser: pdfplumber.PDF,
        page_num: int,
        document_name: str
    ) -> list[DocEntity]:
        try:
            table_page = table_parser.pages[page_num]
            tables = table_page.extract_tables()

            return [
                TableDocEntity(
                    position=EntityPosition(document_name, page_num),
                    table=self._process_table(table),
                )
                for table in tables
            ]
        except Exception as exc:
            raise ExtractTablesError from exc

    def _extract_text_block(
        self,
        element: LTTextContainer,  # type: ignore
        page_num: int,
        document_name: str
    ) -> TextDocEntity:
        try:
            text = element.get_text().strip().replace("\n", "")
            return TextDocEntity(
                position=EntityPosition(document_name, page_num),
                text=text
            )
        except Exception as exc:
            raise ExtractTextBlockError from exc

    def _extract_image(
        self,
        pdf_object: PyPDF2.PdfReader,
        element: LTFigure,
        page_num: int,
        document_name: str
    ) -> ImageDocEntity:
        try:
            page_object = pdf_object.pages[page_num]
            image = self._crop_image_from_pdf(element, page_object)
            return ImageDocEntity(
                position=EntityPosition(document_name=document_name, page_number=page_num),
                image=image
            )
        except Exception as exc:
            raise ExtractImageError from exc

    def read(
        self,
        file: io.IOBase | str,
        filename: str | None = None
    ) -> tuple[ProcessedDocument, list[Exception]]:
        if isinstance(file, str):
            pdf_file = open(file, "rb")
            filename = filename if filename else Path(file).stem
        else:
            assert filename is not None, "param filename should be specified if file is a file object"
            pdf_file = file  # type: ignore
        return self.process_pdf_bytes(pdf_file, filename)

    def process_pdf_bytes(self, pdf_file: io.IOBase, document_name: str) -> tuple[ProcessedDocument, list[Exception]]:
        errors = []
        doc_entities: list[DocEntity] = []
        pdf_object = PyPDF2.PdfReader(pdf_file)  # type: ignore
        table_parser = pdfplumber.open(pdf_file)  # type: ignore

        for page_num, page in enumerate(extract_pages(pdf_file)):
            try:
                page_entities = self._extract_tables(table_parser, page_num, document_name)
            except Exception as err:
                errors.append(err)

            for element in page._objs:
                if isinstance(element, LTTextContainer):
                    try:
                        text_entity = self._extract_text_block(element, page_num, document_name)
                        if text_entity.text:
                            page_entities.append(text_entity)
                    except Exception as err:
                        errors.append(err)
                elif isinstance(element, LTFigure):
                    try:
                        page_entities.append(
                            self._extract_image(pdf_object, element, page_num, document_name)
                        )
                    except Exception as err:
                        errors.append(err)

            doc_entities.extend(page_entities)

        return ProcessedDocument(
            name=document_name,
            num_pages=len(pdf_object.pages),
            original_format="pdf",
            entities=doc_entities
        ), errors
