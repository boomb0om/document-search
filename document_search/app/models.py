from pydantic import BaseModel, Field


class StorageItemResponse(BaseModel):
    document_id: str
    document_filename: str
    num_pages: int


class StorageInfoResponse(BaseModel):
    items: list[StorageItemResponse]
    total_documents: int


class SearchQuery(BaseModel):
    query: str = Field(description="Query to search for")
    top_k: int = Field(default=5, description="Number of relevant documents to return")
    document_ids: list[str] | None = Field(default=None, description="List of document IDs to search")


class SearchResultItem(BaseModel):
    document_id: str
    page: int
    text: str
    relevance_score: float


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResultItem]
