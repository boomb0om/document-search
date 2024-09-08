from typing import Protocol, Optional
import io

from document_search.entities import ProcessedDocument
from .doc_reader_interface import IDocumentReader


class DocxDocumentReader(IDocumentReader):
    
    def read(
        self, 
        file: io.IOBase | str, 
        filename: Optional[str] = None
    ) -> tuple[ProcessedDocument, list[Exception]]:
        raise NotImplementedError()