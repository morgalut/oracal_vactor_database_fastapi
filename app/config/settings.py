from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from pathlib import Path
from typing import Optional
import logging

# === Setup ===
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"

logger = logging.getLogger(__name__)


# =======================
# ✅ Vector Settings
# =======================
class VectorSettings(BaseSettings):
    # === Oracle DB Credentials ===
    db_dsn: str = Field(..., env="DB_DSN")
    db_user: str = Field(..., env="DB_USER")
    oracle_password: str = Field(..., env="ORACLE_PASSWORD")

    # === Vector Store Config ===
    embedding_model: str = Field(default="all-MiniLM-L6-v2", env="EMBEDDING_MODEL")
    vector_dimension: int = Field(default=384, env="VECTOR_DIMENSION")
    table_name: str = Field(default="documents_vectors", env="TABLE_NAME")

    # === Pydantic Config ===
    model_config = SettingsConfigDict(
        env_prefix="",
        env_file=str(ENV_FILE),
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("vector_dimension")
    @classmethod
    def check_dimension(cls, v):
        if v <= 0:
            raise ValueError("VECTOR_DIMENSION must be a positive integer.")
        return v


# =======================
# ✅ Database Connection Settings
# =======================
class DatabaseSettings(BaseSettings):
    oracle_pwd: Optional[str] = Field(None, alias="ORACLE_PWD")
    dsn: str = Field(..., alias="DB_DSN")
    wallet_location: Optional[str] = Field(None, alias="DB_WALLET_LOCATION")
    use_resource_principal: bool = Field(False, alias="DB_USE_RESOURCE_PRINCIPAL")

    model_config = SettingsConfigDict(
        env_prefix="",
        env_file=str(ENV_FILE),
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("dsn")
    @classmethod
    def check_dsn(cls, v):
        if not v or "/" not in v:
            raise ValueError("DB_DSN must be a valid Oracle DSN like 'host:port/service'")
        return v


# =======================
# ✅ Settings Validator
# =======================
def validate_settings() -> VectorSettings:
    """Raise early if any required VectorSettings are missing or invalid."""
    try:
        settings = VectorSettings()
        missing = []

        if not settings.db_dsn:
            missing.append("DB_DSN")
        if not settings.db_user:
            missing.append("DB_USER")
        if not settings.oracle_password:
            missing.append("ORACLE_PASSWORD")

        if missing:
            logger.error(f"❌ Missing required environment variables: {', '.join(missing)}")
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

        logger.info("✅ Loaded and validated VectorSettings.")
        return settings

    except Exception as e:
        logger.exception("❌ Failed to validate VectorSettings.")
        raise


# =======================
# ✅ Debug Utility
# =======================
def log_loaded_settings():
    """Print current configuration to stdout and logs for debug visibility."""
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
            print(line)

    except Exception as e:
        logger.warning(f"⚠️ Config load failed: {e}")
        print(f"⚠️ Config load failed: {e}")
