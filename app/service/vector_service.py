import logging
from typing import Optional, List

from app.db.oracle_vector import OracleVectorClient
from app.config.settings import VectorSettings
from app.model.document import SearchResponse, SearchResult

logger = logging.getLogger(__name__)


class VectorService:
    def __init__(self, settings: Optional[VectorSettings] = None):
        # Load config from .env or inject externally (e.g., for testing)
        self.settings = settings or VectorSettings()
        logger.info(
            f"✅ VectorService initialized — Table: {self.settings.table_name}, Model: {self.settings.embedding_model}"
        )
        self._client: Optional[OracleVectorClient] = None  # Lazy init

    @property
    def client(self) -> OracleVectorClient:
        """Lazily initialize the Oracle vector client."""
        if self._client is None:
            self._client = OracleVectorClient(self.settings)
        return self._client

    def upsert_document(self, doc_id: str, text: str) -> None:
        """Stores or updates a document in the Oracle vector store."""
        logger.info(f"📄 Upserting document ID: {doc_id}")
        try:
            self.client.upsert_document(doc_id, text)
            logger.info(f"✅ Upsert complete for ID: {doc_id}")
        except Exception as e:
            logger.exception(f"❌ Upsert failed for ID: {doc_id}")
            raise RuntimeError(f"Vector upsert failed for '{doc_id}'") from e

    def search_similar_documents(self, query: str, top_k: int = 5) -> SearchResponse:
        """Finds top-k most similar documents based on semantic meaning."""
        logger.info(f"🔍 Searching top-{top_k} results for query: '{query}'")
        try:
            matches = self.client.search(query, top_k)
            results: List[SearchResult] = [
                SearchResult(
                    id=doc.metadata.get("id", "unknown"),
                    text=doc.page_content,
                    score=round(doc.score, 4) if doc.score is not None else None
                )
                for doc in matches
            ]
            logger.info(f"✅ Search returned {len(results)} results for query: '{query}'")
            return SearchResponse(results=results)
        except Exception as e:
            logger.exception(f"❌ Search error for query: '{query}'")
            raise RuntimeError(f"Vector search failed for query: '{query}'") from e
