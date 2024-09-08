from dataclasses import dataclass
from typing import Any, Literal

import numpy as np
from PIL import Image


@dataclass
class EntityPosition:
    page_number: int

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, EntityPosition) and self.page_number == other.page_number
        )

    def __hash__(self) -> int:
        return hash(self.page_number)

    def __str__(self) -> str:
        return f"Page Number: {self.page_number}"


@dataclass
class DocEntity:
    position: EntityPosition


@dataclass
class ProcessedDocument:
    name: str
    num_pages: int
    original_format: Literal["", "pdf", "docx"]
    entities: list[DocEntity]
    page_entities: dict[int, list[DocEntity]]

    @classmethod
    def empty(cls) -> "ProcessedDocument":
        return cls(
            name="", num_pages=0, original_format="", entities=[], page_entities={}
        )


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
