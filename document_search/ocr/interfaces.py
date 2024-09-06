from typing import Protocol

from document_search import ProcessedDocument


class DocumentReader(Protocol):

    def process_pdf(self, document_path: str) -> ProcessedDocument: ...

    def process_docx(self, document_path: str) -> ProcessedDocument: ...
