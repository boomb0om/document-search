from dataclasses import dataclass

import numpy as np
from PIL import Image

from .types import DocumentFormat


@dataclass
class EntityPosition:
    document_name: str
    page_number: int
    document_id: str | None = None

    def __str__(self) -> str:
        return f"(document_id={self.document_id}, document_name={self.document_name}, page={self.page_number})"


@dataclass
class DocEntity:
    position: EntityPosition


@dataclass
class ProcessedDocument:
    name: str
    num_pages: int
    original_format: DocumentFormat
    entities: list[DocEntity]

    def get_entities_on_page(self, page: int) -> list[DocEntity]:
        return [entity for entity in self.entities if entity.position.page_number == page]


@dataclass
class TextDocEntity(DocEntity):
    position: EntityPosition
    text: str


@dataclass
class TableDocEntity(DocEntity):
    position: EntityPosition
    table: list[list[str]]


@dataclass
class ImageDocEntity(DocEntity):
    position: EntityPosition
    image: Image.Image


@dataclass
class VectorizedDocEntity(DocEntity):
    vector: np.ndarray  # type: ignore


@dataclass
class VectorizedDocument:
    name: str
    id_: str
    entities: list[VectorizedDocEntity]


@dataclass
class TextDocument:
    name: str
    id_: str
    entities: list[TextDocEntity]
