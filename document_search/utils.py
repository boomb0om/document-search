import io

from PIL import Image

from document_search.ocr import DocumentReader
from document_search.types import DocumentFormat


def extract_image_from_file(
    document_bytes: io.BytesIO,
    format: DocumentFormat,
    page: int
) -> Image.Image:
    doc_reader = DocumentReader()
    return doc_reader.extract_page_as_image(document_bytes, format, page)
