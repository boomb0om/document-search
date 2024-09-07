import unittest
import numpy as np
from document_search.entities import EntityPosition, TextDocEntity
from document_search.search.embedders import TextEntityEmbedderE5


class TestTextEntityEmbedderE5(unittest.TestCase):

    def test_vectorize(self):
        position = EntityPosition(parent_document_id="doc1", page=1, position_x=0.5, position_y=0.5)
        text_entity = TextDocEntity(id_=1, position=position, text="This is a sample text")

        embedder = TextEntityEmbedderE5()

        vectorized_entity = embedder.vectorize(text_entity)

        self.assertEqual(vectorized_entity.id_, text_entity.id_)
        self.assertEqual(vectorized_entity.position, text_entity.position)

        self.assertIsInstance(vectorized_entity.vector, np.ndarray)
        self.assertEqual(vectorized_entity.vector.shape,
                         (1, 768))


if __name__ == '__main__':
    unittest.main()
