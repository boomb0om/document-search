from typing import Protocol, Optional
import io

from document_search.entities import ProcessedDocument


class IDocumentReader(Protocol):
    
    def read(
        self, 
        file: io.IOBase | str, 
        filename: Optional[str] = None
    ) -> tuple[ProcessedDocument, list[Exception]]: ...