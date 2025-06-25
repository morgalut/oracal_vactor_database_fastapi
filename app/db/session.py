import logging
import oracledb
from app.config.settings import DatabaseSettings

logger = logging.getLogger(__name__)


def get_db_session() -> oracledb.Connection:
    """
    Initializes and returns a live Oracle DB session based on config.
    Supports both resource principal and wallet-based auth.
    """
    settings = DatabaseSettings()

    try:
        if settings.use_resource_principal:
            logger.info("🔐 Using OCI resource principal authentication.")
            try:
                from ads.common.auth import ResourcePrincipalAuth
            except ImportError as e:
                raise ImportError("❌ 'oracle-ads' is required for resource principal auth.") from e

            auth = ResourcePrincipalAuth()
            token = auth.security_token

            conn = oracledb.connect(
                externalauth=True,
                dsn=settings.dsn,
                access_token=token,
                wallet_location=settings.wallet_location
            )
        else:
            logger.info(f"🔗 Connecting using wallet auth to DSN: {settings.dsn}")
            conn = oracledb.connect(
                dsn=settings.dsn,
                wallet_location=settings.wallet_location
            )

        logger.info("✅ Oracle DB session established successfully.")
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
