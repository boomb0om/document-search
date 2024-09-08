import numpy as np
from langchain_community.embeddings import HuggingFaceEmbeddings  # type: ignore

from document_search.entities import TextDocEntity, VectorizedDocEntity
from document_search.search.interfaces import TextEntityEmbedder


class TextEntityEmbedderE5(TextEntityEmbedder):

    def __init__(self) -> None:
        self.embedder = HuggingFaceEmbeddings(
            model_name='intfloat/multilingual-e5-base',
            encode_kwargs={'normalize_embeddings': True}
        )
        self.embed_shape = 768

    def vectorize(self, item: TextDocEntity) -> VectorizedDocEntity:
        vector = np.array(self.embedder.embed_documents([item.text]))

        return VectorizedDocEntity(
            position=item.position,
            vector=vector
        )
