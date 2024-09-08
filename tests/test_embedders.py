import numpy as np
from document_search.entities import EntityPosition, TextDocEntity
from document_search.search.embedders import TextEntityEmbedderE5

def test_vectorize():
    position = EntityPosition(parent_document_id="doc1", page=1, position_x=0.5, position_y=0.5)
    text_entity = TextDocEntity(id_=1, position=position, text="This is a sample text")

    embedder = TextEntityEmbedderE5()

    vectorized_entity = embedder.vectorize(text_entity)

    assert vectorized_entity.id_ == text_entity.id_
    assert vectorized_entity.position == text_entity.position

    assert isinstance(vectorized_entity.vector, np.ndarray)
    assert vectorized_entity.vector.shape == (1, 768)