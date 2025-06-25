import threading
import logging
from functools import lru_cache
from typing import Optional

from .base_client import OracleVectorClient
from app.config.settings import VectorSettings

logger = logging.getLogger(__name__)

_lock = threading.Lock()
_instance: Optional[OracleVectorClient] = None


def get_oracle_vector_client() -> OracleVectorClient:
    """Thread-safe, lazily-initialized singleton OracleVectorClient."""
    global _instance
    if _instance is None:
        with _lock:
            if _instance is None:
                logger.info("🧠 Initializing OracleVectorClient singleton instance...")
                try:
                    settings = VectorSettings()
                    _instance = OracleVectorClient(settings)
                    logger.info("✅ OracleVectorClient initialized.")
                except Exception as e:
                    logger.exception("❌ Failed to initialize OracleVectorClient.")
                    raise RuntimeError("Could not initialize vector client") from e
            else:
                logger.debug("♻️ OracleVectorClient already initialized (post-lock).")
    else:
        logger.debug("♻️ Reusing existing OracleVectorClient instance.")
    return _instance
