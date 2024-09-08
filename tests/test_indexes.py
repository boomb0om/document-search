import pytest
from langchain_community.embeddings import HuggingFaceEmbeddings  # type: ignore
from document_search.entities import TextDocEntity, EntityPosition, TextDocument
from document_search.storages.indexes import DocumentStorageE5, TextEntityEmbedderE5


@pytest.fixture
def embedder():
    return TextEntityEmbedderE5()


@pytest.fixture
def document_storage(embedder):
    return DocumentStorageE5(embedder)


def test_add_document(document_storage):
    entities = [TextDocEntity(position=EntityPosition(1), text="Test text 1"),
                TextDocEntity(position=EntityPosition(2), text="Test text 2")]
    vectorized_document = TextDocument(entities=entities, id_="", name="")

    document_storage.add_document(vectorized_document)

    assert document_storage.document_counter == 2


def test_get_relevant_entities(document_storage):
    entities = [TextDocEntity(position=EntityPosition(1), text="Test text 1"),
                TextDocEntity(position=EntityPosition(2), text="Test text 2")]
    vectorized_document = TextDocument(entities=entities, id_="", name="")
    document_storage.add_document(vectorized_document)

    query = "Test text 1"
    relevant_docs = document_storage.get_relevant_entities(query, k=1)

    assert len(relevant_docs) == 1
    assert relevant_docs[0].position == EntityPosition(1)
    assert relevant_docs[0].text == "Test text 1"
