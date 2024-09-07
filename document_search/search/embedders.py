from document_search.entities import TextDocEntity, VectorizedDocEntity
from document_search.search.interfaces import TextEntityEmbedder
import numpy as np
from langchain_community.embeddings import HuggingFaceEmbeddings


class TextEntityEmbedderE5(TextEntityEmbedder):

    def __init__(self):
        self.embedder = HuggingFaceEmbeddings(model_name='intfloat/multilingual-e5-base')

    def vectorize(self, item: TextDocEntity) -> VectorizedDocEntity:
        vector = np.array(self.embedder.embed_documents([item.text]))

        return VectorizedDocEntity(
            id_=item.id_,
            position=item.position,
            vector=vector
        )


if __name__ == "__main__":
    from document_search.entities import EntityPosition, TextDocEntity

    position = EntityPosition(parent_document_id="doc1", page=1, position_x=0.5, position_y=0.5)
    text_entity = TextDocEntity(id_=1, position=position, text="Раз два три четыре")

    embedder = TextEntityEmbedderE5()
    vectorized_entity = embedder.vectorize(text_entity)
    print(vectorized_entity)
