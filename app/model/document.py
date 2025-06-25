from pydantic import BaseModel
from typing import List, Optional


class DocumentUpsertRequest(BaseModel):
    id: str
    text: str


class DocumentResponse(BaseModel):
    id: str
    status: str


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


class SearchResult(BaseModel):
    id: str
    text: str
    score: Optional[float] = None


class SearchResponse(BaseModel):
    results: List[SearchResult]
