from fastapi import APIRouter

from app.pipeline import query_pipeline
from app.schemas import QueryRequest, QueryResponse

router = APIRouter(prefix="/query", tags=["query"])


@router.post("", response_model=QueryResponse)
def query(req: QueryRequest):
    result = query_pipeline(query=req.query, top_k=req.top_k, max_tokens=req.max_tokens)
    return QueryResponse(**result)
