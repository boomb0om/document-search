from pathlib import Path

import fitz
import pdfplumber
import PyPDF2
from loguru import logger
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

from .exceptions import (
    ConvertToImagesError,
    ExtractImageError,
    ExtractTablesError,
    ExtractTextBlockError,
)


class DocumentReader:
    def convert_pdf_to_images(self, pdf_path: str) -> list[Image.Image]:
        try:
            with fitz.open(pdf_path) as pdf_document:

                def get_image(page_number: int) -> Image.Image:
                    page = pdf_document.load_page(page_number)
                    pix = page.get_pixmap()
                    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)

                return list(map(get_image, range(len(pdf_document))))
        except Exception as exc:
            logger.exception(exc)
            return []

    def _crop_image_from_pdf(
        self, element: LTFigure, page_object: PyPDF2.PageObject
    ) -> Image.Image:
        page_object.mediabox.lower_left = [element.x0, element.y0]
        page_object.mediabox.upper_right = [element.x1, element.y1]

        pdf_writer = PyPDF2.PdfWriter()
        pdf_writer.add_page(page_object)

        tmp_pdf_path = "__tmp_cropped_image_file.pdf"
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
    ) -> list[DocEntity]:
        try:
            table_page = table_parser.pages[page_num]
            tables = table_page.extract_tables()

            return [
                TableDocEntity(
                    position=EntityPosition(page_number=page_num),
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
    ) -> TextDocEntity:
        try:
            text = element.get_text().strip().replace("\n", "")
            return TextDocEntity(position=EntityPosition(page_num), text=text)
        except Exception as exc:
            raise ExtractTextBlockError from exc

    def _extract_image(
        self, pdf_object: PyPDF2.PdfReader, element: LTFigure, page_num: int
    ) -> ImageDocEntity:
        try:
            page_object = pdf_object.pages[page_num]
            image = self._crop_image_from_pdf(element, page_object)
            return ImageDocEntity(
                position=EntityPosition(page_number=page_num), image=image
            )
        except Exception as exc:
            raise ExtractImageError from exc

    def process_pdf(self, document_path: str) -> ProcessedDocument:
        try:
            with open(document_path, "rb") as pdf_file:
                doc_entities: list[DocEntity] = []
                page_entities_mapping: dict[int, list[DocEntity]] = {}
                pdf_object = PyPDF2.PdfReader(pdf_file)
                table_parser = pdfplumber.open(pdf_file)

                for page_num, page in enumerate(extract_pages(document_path)):
                    page_entities = self._extract_tables(table_parser, page_num)

                    for element in page._objs:
                        if isinstance(element, LTTextContainer):
                            text_entity = self._extract_text_block(element, page_num)
                            if text_entity.text:
                                page_entities.append(text_entity)

                        elif isinstance(element, LTFigure):
                            page_entities.append(
                                self._extract_image(pdf_object, element, page_num)
                            )

                    page_entities_mapping[page_num] = page_entities
                    doc_entities.extend(page_entities)

                return ProcessedDocument(
                    name=Path(document_path).stem,
                    num_pages=len(pdf_object.pages),
                    original_format="pdf",
                    entities=doc_entities,
                    page_entities=page_entities_mapping,
                )
        except ConvertToImagesError as exc:
            logger.exception(exc)
        except ExtractTablesError as exc:
            logger.exception(exc)
        except ExtractTextBlockError as exc:
            logger.exception(exc)
        except ExtractImageError as exc:
            logger.exception(exc)
        except Exception as exc:
            logger.exception(exc)

        return ProcessedDocument.empty()

    def process_docx(self, document_path: str) -> ProcessedDocument:
        raise NotImplementedError
