from fastapi import APIRouter

from app.pipeline import ingest_pipeline
from app.schemas import IngestRequest, IngestResponse

router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post("", response_model=IngestResponse)
def ingest(req: IngestRequest):
    result = ingest_pipeline(num_dummy_pdfs=req.num_dummy_pdfs, force_regenerate=req.force_regenerate)
    return IngestResponse(**result)
