from dataclasses import dataclass
from typing import Literal

import numpy as np
from PIL import Image


@dataclass
class EntityPosition:
    parent_document_id: str
    page: int
    position_x: float
    position_y: float


@dataclass
class DocEntity:
    id_: int
    position: EntityPosition


@dataclass
class ProcessedDocument:
    name: str
    id_: str
    num_pages: int
    original_format: Literal['pdf', 'docx']
    entities: list[DocEntity]


@dataclass
class TextDocEntity(DocEntity):
    id_: int
    position: EntityPosition
    text: str


@dataclass
class TableDocEntity(DocEntity):
    id_: int
    position: EntityPosition
    table: str


@dataclass
class ImageDocEntity(DocEntity):
    id_: int
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
