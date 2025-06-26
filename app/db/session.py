import logging
import oracledb
from app.config.settings import DatabaseSettings

logger = logging.getLogger(__name__)


def get_db_session():
    from app.config.settings import VectorSettings
    settings = VectorSettings()

    if not settings.db_dsn or not settings.db_user or not settings.oracle_password:
        logger.error("❌ Missing Oracle DB credentials (DSN, USER, PASSWORD)")
        raise RuntimeError("Oracle DB credentials are incomplete")

    try:
        logger.info(f"🔌 Connecting to Oracle: {settings.db_dsn}")
        conn = oracledb.connect(
            user=settings.db_user,
            password=settings.oracle_password,
            dsn=settings.db_dsn
        )
        return conn
    except Exception as e:
        logger.exception("❌ Failed to establish Oracle DB session.")
        raise RuntimeError("Could not establish Oracle DB connection") from e



def check_db_connection() -> bool:
    """
    Checks whether the Oracle DB is reachable and responsive.
    Returns True if the connection test succeeds, False otherwise.
    """
    logger.info("🔍 Performing Oracle DB connection health check...")
    try:
        with get_db_session() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1 FROM DUAL")
                result = cursor.fetchone()
                if result and result[0] == 1:
                    logger.info("✅ Oracle DB health check passed.")
                    return True
    except Exception as e:
        logger.warning(f"⚠️ Oracle DB health check failed: {e}")
    return False
