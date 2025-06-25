import pytest
from unittest.mock import MagicMock, patch
from service.vector_service import VectorService

@pytest.fixture
def mock_vector_client():
    return MagicMock()

@patch("service.vector_service.OracleVectorClient")
def test_upsert_success(mock_client):
    service = VectorService()
    service.client = mock_client
    
    service.upsert_document("doc1", "Hello World")
    mock_client.upsert_document.assert_called_once_with("doc1", "Hello World")

@patch("service.vector_service.OracleVectorClient")
def test_upsert_failure(mock_client):
    mock_client.upsert_document.side_effect = Exception("DB Error")
    service = VectorService()
    service.client = mock_client
    
    with pytest.raises(Exception):
        service.upsert_document("doc1", "Hello World")