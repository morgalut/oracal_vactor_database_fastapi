import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from starlette.status import HTTP_200_OK

from app.router.upsert import router as upsert_router
from app.router.search import router as search_router
from app.router.health import router as health_router
from app.config.settings import log_loaded_settings  # ✅ Config print + logging

# --- Logging setup ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- FastAPI App Configuration ---
app = FastAPI(
    title="Oracle Vector API",
    description="An API for managing and searching document vectors in Oracle using LangChain + FastAPI.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# --- CORS Configuration ---
def get_allowed_origins() -> list[str]:
    """Read allowed CORS origins from environment or default to wildcard."""
    origins = os.getenv("ALLOWED_ORIGINS", "*")
    return origins.split(",") if origins != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers ---
app.include_router(upsert_router, prefix="/vector", tags=["Vector Upsert"])
app.include_router(search_router, prefix="/vector", tags=["Vector Search"])
app.include_router(health_router, tags=["System"])  # ✅ Already contains /health

# --- Startup / Shutdown Lifecycle Hooks ---
@app.on_event("startup")
async def startup_event():
    log_loaded_settings()  # ✅ Print & log env + DB config
    logger.info("🚀 Oracle Vector API started successfully.")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Oracle Vector API shutting down.")
