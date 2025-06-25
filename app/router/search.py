from fastapi import APIRouter, HTTPException, status, Depends
import logging

from app.model.document import SearchRequest, SearchResponse
from app.service.vector_service import VectorService

logger = logging.getLogger(__name__)
router = APIRouter()

def get_vector_service() -> VectorService:
    return VectorService()

@router.post(
    "/search",
    response_model=SearchResponse,
    status_code=200,
    summary="Search for similar documents",
    description="Performs vector similarity search and returns the closest matching documents."
)
async def search_documents(
    request: SearchRequest,
    vector_service: VectorService = Depends(get_vector_service)
):
    try:
        response = vector_service.search_similar_documents(
            query=request.query,
            top_k=request.top_k
        )
        logger.info(f"✅ Search returned {len(response.results)} results.")
        return response
    except Exception as e:
        logger.exception(f"❌ Vector search error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )
