# app/db/oracle_vector.py

import logging
from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document
from langchain_community.vectorstores import OracleVS

from app.config.settings import VectorSettings
from app.db.session import get_db_session

logger = logging.getLogger(__name__)


# === Custom HuggingFace Embedding Wrapper ===
class HFEmbeddings(Embeddings):
    def __init__(self, model_name: str, expected_dim: int):
        self.model = SentenceTransformer(model_name)
        self.expected_dim = expected_dim

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        embeddings = self.model.encode(texts, show_progress_bar=False)
        for i, emb in enumerate(embeddings):
            if len(emb) != self.expected_dim:
                raise ValueError(f"Embedding dimension mismatch for doc {i}: {len(emb)} vs {self.expected_dim}")
        return embeddings.tolist() if hasattr(embeddings, "tolist") else embeddings

    def embed_query(self, query: str) -> List[float]:
        vec = self.model.encode(query)
        if len(vec) != self.expected_dim:
            raise ValueError(f"Query embedding dimension mismatch: got {len(vec)}, expected {self.expected_dim}")
        return vec.tolist() if hasattr(vec, "tolist") else list(vec)



# === Oracle Vector Client ===
class OracleVectorClient:
    def __init__(self, settings: VectorSettings):
        self.settings = settings
        self.connection = get_db_session()

        logger.info(f"🔧 Using HF model: {self.settings.embedding_model}")
        self._embedding_model = self._init_embedding_model()

        logger.info("📦 Initializing OracleVS vector store...")
        self._vector_store = self._init_vector_store()

    def _init_embedding_model(self) -> HFEmbeddings:
        try:
            return HFEmbeddings(
                model_name=self.settings.embedding_model,
                expected_dim=self.settings.vector_dimension
            )
        except Exception as e:
            logger.exception("❌ Failed to initialize HFEmbeddings.")
            raise RuntimeError("Embedding model initialization failed") from e

    def _init_vector_store(self) -> OracleVS:
        try:
            return OracleVS(
                client=self.connection,
                table_name=self.settings.table_name,
                embedding_function=self._embedding_model
            )
        except Exception as e:
            logger.exception("❌ Failed to initialize OracleVS vector store.")
            raise RuntimeError("Vector store initialization failed") from e

    def upsert_document(self, doc_id: str, text: str) -> None:
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
        try:
            logger.info(f"🔍 Performing similarity search for query: '{query}' (top_k={top_k})")
            return self._vector_store.similarity_search_with_score(query, k=top_k)
        except Exception as e:
            logger.exception("❌ Similarity search failed.")
            raise RuntimeError("Vector similarity search failed") from e

    def _ensure_table_exists(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT table_name FROM user_tables WHERE table_name = :1", [self.settings.table_name.upper()])
        exists = cursor.fetchone()
        if not exists:
            raise RuntimeError(f"Table {self.settings.table_name} does not exist in Oracle DB")
