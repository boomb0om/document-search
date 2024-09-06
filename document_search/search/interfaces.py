from typing import Protocol

from document_search import TextDocEntity, VectorizedDocEntity


class TextEntityEmbedder(Protocol):

    def vectorize(self, item: TextDocEntity) -> VectorizedDocEntity: ...
