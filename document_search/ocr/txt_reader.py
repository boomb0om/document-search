import io

from document_search.entities import ProcessedDocument

from .doc_reader_interface import IDocumentReader


class TxtDocumentReader(IDocumentReader):

    def read(
        self,
        file: io.IOBase | str,
        filename: str | None = None
    ) -> tuple[ProcessedDocument, list[Exception]]:
        raise NotImplementedError()
