from fastapi import APIRouter, HTTPException, status, Depends
import logging

from app.model.document import DocumentUpsertRequest, DocumentResponse
from app.service.vector_service import VectorService

logger = logging.getLogger(__name__)
router = APIRouter()


def get_vector_service() -> VectorService:
    return VectorService()

@router.post(
    "/documents",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upsert a document vector",
    description="Inserts or updates a document vector in the Oracle vector store."
)
async def upsert_document(
    request: DocumentUpsertRequest,
    vector_service: VectorService = Depends(get_vector_service)
):
    try:
        vector_service.upsert_document(request.id, request.text)
        logger.info(f"✅ Document upserted: {request.id}")
        return DocumentResponse(id=request.id, status="success")
    except Exception as e:
        logger.exception(f"❌ Failed to upsert document: {request.id} — {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Vector upsert failed: {str(e)}"
        )
