from fastapi import APIRouter
from app.db.session import check_db_connection

router = APIRouter()

@router.get("/health", tags=["System"])
def health_check():
    """
    Health check endpoint with real Oracle DB connection test.
    """
    db_ok = check_db_connection()
    return {
        "status": "healthy" if db_ok else "degraded",
        "db_connection": db_ok
    }
