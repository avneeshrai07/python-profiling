"""Pydantic request/response models for the API."""
from typing import Optional

from pydantic import BaseModel


class IngestRequest(BaseModel):
    num_dummy_pdfs: int = 12
    force_regenerate: bool = False


class IngestResponse(BaseModel):
    documents_loaded: int
    chunks_indexed: int
    elapsed_seconds: float


class QueryRequest(BaseModel):
    query: str
    top_k: int = 5
    max_tokens: int = 80


class SourceChunk(BaseModel):
    doc_id: str
    chunk_id: int
    score: float
    snippet: str


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]
    retrieval_seconds: float
    generation_seconds: float


class TaskResult(BaseModel):
    task: str
    elapsed_seconds: float
    detail: Optional[dict] = None
