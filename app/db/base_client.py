from abc import ABC, abstractmethod
from typing import List
import logging

from langchain_community.vectorstores.oraclevs import OracleVS
from langchain_community.embeddings import OracleEmbeddings
from langchain_core.documents import Document
from app.config.settings import VectorSettings
from .session import get_db_session

logger = logging.getLogger(__name__)


class BaseVectorClient(ABC):
    def __init__(self, settings: VectorSettings):
        self.settings = settings
        self.embedding_model = self._init_embedding_model()

    @abstractmethod
    def upsert_document(self, doc_id: str, text: str) -> None:
        raise NotImplementedError("Subclasses must implement `upsert_document` method.")

    @abstractmethod
    def search(self, query: str, top_k: int) -> List[Document]:
        raise NotImplementedError("Subclasses must implement `search` method.")

    def _init_embedding_model(self) -> OracleEmbeddings:
        try:
            logger.info(f"🔧 Initializing embedding model: {self.settings.embedding_model}")
            return OracleEmbeddings(model_name=self.settings.embedding_model)
        except Exception as e:
            logger.exception("❌ Failed to initialize OracleEmbeddings.")
            raise RuntimeError("Embedding model initialization failed") from e


class OracleVectorClient(BaseVectorClient):
    def __init__(self, settings: VectorSettings):
        super().__init__(settings)
        self._vector_store = self._init_vector_store()

    def _init_vector_store(self) -> OracleVS:
        try:
            logger.info(f"🔌 Connecting to Oracle Vector Store: {self.settings.table_name}")
            return OracleVS(
                client=get_db_session(),
                table_name=self.settings.table_name,
                embedding_function=self.embedding_model,
                dimension=self.settings.vector_dimension
            )
        except Exception as e:
            logger.exception("❌ Failed to initialize OracleVS vector store.")
            raise RuntimeError("Vector store initialization failed") from e

    def upsert_document(self, doc_id: str, text: str) -> None:
        """Insert or update a vectorized document."""
        try:
            logger.info(f"📥 Upserting document ID: {doc_id}")
            metadata = {"id": doc_id}
            self._vector_store.add_texts(
                texts=[text],
                metadatas=[metadata],
                ids=[doc_id],
                upsert=True
            )
            logger.info(f"✅ Upserted document: {doc_id}")
        except Exception as e:
            logger.exception(f"❌ Upsert failed for ID: {doc_id}")
            raise RuntimeError(f"Vector upsert failed for ID: {doc_id}") from e

    def search(self, query: str, top_k: int = 5) -> List[Document]:
        """Perform semantic search on vector store."""
        try:
            logger.info(f"🔍 Performing similarity search for query: '{query}' (top_k={top_k})")
            return self._vector_store.similarity_search_with_score(query, k=top_k)
        except Exception as e:
            logger.exception("❌ Similarity search failed.")
            raise RuntimeError("Vector similarity search failed") from e
