from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from pathlib import Path
from typing import Optional
import logging
import os

# === Determine .env path ===
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"

logger = logging.getLogger(__name__)


class VectorSettings(BaseSettings):
    table_name: str = Field("documents_vectors", alias="VECTOR_TABLE_NAME")
    embedding_model: str = Field("sentence-transformers/all-MiniLM-L6-v2", alias="VECTOR_EMBEDDING_MODEL")
    vector_dimension: int = Field(384, alias="VECTOR_DIMENSION")

    model_config = SettingsConfigDict(
        env_prefix="",
        env_file=str(ENV_FILE),
        case_sensitive=False,
        extra="ignore",  # 👈 optional fallback
    )


    @field_validator("vector_dimension")
    @classmethod
    def check_dimension(cls, v):
        if v <= 0:
            raise ValueError("VECTOR_DIMENSION must be a positive integer.")
        return v


class DatabaseSettings(BaseSettings):
    oracle_pwd: Optional[str] = Field(None, alias="ORACLE_PWD")
    dsn: str = Field(..., alias="DB_DSN")
    wallet_location: Optional[str] = Field(None, alias="DB_WALLET_LOCATION")
    use_resource_principal: bool = Field(False, alias="DB_USE_RESOURCE_PRINCIPAL")

    model_config = SettingsConfigDict(
        env_prefix="",
        env_file=str(ENV_FILE),
        case_sensitive=False,
        extra="ignore",  # 👈 optional if you still want to ignore extras
    )


    @field_validator("dsn")
    @classmethod
    def check_dsn(cls, v):
        if not v or "/" not in v:
            raise ValueError("DB_DSN must be a valid Oracle DSN like 'host:port/service'")
        return v


def log_loaded_settings():
    """Utility to log and print current settings for debug visibility."""
    try:
        vconf = VectorSettings()
        dconf = DatabaseSettings()

        msg = [
            "✅ Loaded configuration from .env",
            f"📦 VECTOR_TABLE     = {vconf.table_name}",
            f"🧠 EMBEDDING_MODEL  = {vconf.embedding_model}",
            f"📐 VECTOR_DIMENSION = {vconf.vector_dimension}",
            f"🔗 DB_DSN           = {dconf.dsn}",
            f"🗂️  WALLET_LOCATION = {dconf.wallet_location}",
            f"🔒 USE_RP_AUTH      = {dconf.use_resource_principal}",
        ]

        for line in msg:
            logger.info(line)
            print(line)  # ✅ Ensure visibility without log setup

    except Exception as e:
        logger.warning(f"⚠️ Config load failed: {e}")
        print(f"⚠️ Config load failed: {e}")
