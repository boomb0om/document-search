from typing import Optional
from pathlib import Path
import os
import io

from document_search.entities import ProcessedDocument

from .doc_reader_interface import IDocumentReader
from .pdf_doc_reader import PDFDocumentReader
from .docx_doc_reader import DocxDocumentReader


class DocumentReader(IDocumentReader):

    def __init__(self):
        self.docx_reader = DocxDocumentReader()
        self.pdf_reader = PDFDocumentReader()
        self.format2reader = {
            'pdf': self.pdf_reader,
            'docx': self.docx_reader,
            'doc': self.docx_reader,
        }
    
    def read(
        self, 
        file: io.IOBase | str, 
        filename: Optional[str] = None
    ) -> tuple[ProcessedDocument, list[Exception]]:
        if isinstance(file, str):
            file_obj = open(file, "rb")
            filename = filename if filename else os.path.basename(file)
        else:
            assert filename is not None, "param filename should be specified if file is a file object"
            file_obj = file

        ext = filename.split('.')[-1].lower()
        if ext not in self.format2reader:
            raise ValueError(f"Unsupported file format: {ext}")

        return self.format2reader[ext].read(file_obj, filename)