import io
import os

import requests

API_URL = os.environ["API_URL"]


def add_document(file: io.BytesIO) -> dict:
    response = requests.put(f"{API_URL}/documents/add/", files={"file": file})
    return response.json()


def get_uploading_status(doc_id: str) -> dict:
    response = requests.get(
        f"{API_URL}/documents/status/", params={"documentID": doc_id}
    )
    return response.json()


def get_storage_info() -> dict:
    response = requests.get(f"{API_URL}/documents/storage_info/")
    return response.json()


def search_query(query: str, document_ids: list[str]) -> dict:
    response = requests.post(
        f"{API_URL}/search/query/", json={"query": query, "document_ids": document_ids}
    )
    return response.json()
