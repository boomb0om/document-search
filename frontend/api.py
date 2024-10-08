import io
import os
from typing import Any

import requests

BACKEND_API_URL = os.environ.get("BACKEND_API_URL")


def add_document(file: io.BytesIO) -> Any:
    response = requests.put(f"{BACKEND_API_URL}/documents/add/", files={"file": file})
    return response.json()


def get_uploading_status(doc_id: str) -> Any:
    response = requests.get(
        f"{BACKEND_API_URL}/documents/status/", params={"documentID": doc_id}
    )
    return response.json()


def get_storage_info() -> Any:
    response = requests.get(f"{BACKEND_API_URL}/documents/storage_info/")
    return response.json()


def search_query(query: str, document_ids: list[str] | None, use_rag: bool) -> Any:
    response = requests.post(
        f"{BACKEND_API_URL}/search/query/",
        json={"query": query, "document_ids": document_ids, "use_rag": use_rag},
    )
    return response.json()


def get_image_by_id(document_id: str, page: int) -> io.BytesIO:
    response = requests.get(
        f"{BACKEND_API_URL}/documents/get_image/",
        json={"document_id": document_id, "page": page},
    )
    return io.BytesIO(response.content)
