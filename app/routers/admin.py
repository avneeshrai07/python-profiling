from fastapi import APIRouter

from app.db import count_documents, reset as reset_db
from app.vector_store import STORE

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats")
def stats():
    return {
        "vectors_indexed": len(STORE),
        "documents_in_db": count_documents(),
    }


@router.post("/reset")
def reset():
    STORE.reset()
    reset_db()
    return {"status": "reset"}
