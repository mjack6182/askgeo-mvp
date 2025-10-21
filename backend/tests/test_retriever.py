"""Tests for retriever functionality."""
import pytest
from unittest.mock import Mock, MagicMock
import chromadb
from chromadb.config import Settings as ChromaSettings

from app.rag.retriever import Retriever


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client."""
    client = Mock()

    # Mock embeddings response
    mock_embedding = [0.1] * 1536  # Simulated embedding vector
    client.embeddings.create.return_value = Mock(
        data=[Mock(embedding=mock_embedding)]
    )

    return client


@pytest.fixture
def in_memory_chroma():
    """Create an in-memory ChromaDB client with test data."""
    client = chromadb.Client(ChromaSettings(
        is_persistent=False,
        allow_reset=True
    ))

    # Create collection
    collection = client.create_collection(name="uwp")

    # Add test documents
    test_docs = [
        "UW-Parkside offers undergraduate and graduate programs in business, education, and sciences.",
        "The campus is located in Kenosha, Wisconsin, between Milwaukee and Chicago.",
        "Students can participate in over 70 student organizations and clubs."
    ]

    test_metadatas = [
        {"url": "https://www.uwp.edu/academics", "title": "Academics"},
        {"url": "https://www.uwp.edu/about", "title": "About UWP"},
        {"url": "https://www.uwp.edu/student-life", "title": "Student Life"}
    ]

    # Create simple embeddings (random for testing)
    test_embeddings = [
        [0.1 + i * 0.01] * 1536 for i in range(len(test_docs))
    ]

    collection.add(
        ids=[f"test-{i}" for i in range(len(test_docs))],
        documents=test_docs,
        metadatas=test_metadatas,
        embeddings=test_embeddings
    )

    return client


def test_retriever_query(in_memory_chroma, mock_openai_client):
    """Test that retriever returns relevant chunks."""
    retriever = Retriever(
        chroma_client=in_memory_chroma,
        openai_client=mock_openai_client,
        embed_model="text-embedding-3-small"
    )

    results = retriever.query("What programs does UW-Parkside offer?", k=3)

    # Should return results
    assert len(results) > 0
    assert len(results) <= 3

    # Each result should have required fields
    for result in results:
        assert "text" in result
        assert "url" in result
        assert "title" in result
        assert "score" in result

    # Verify OpenAI client was called
    mock_openai_client.embeddings.create.assert_called_once()


def test_retriever_has_confident_match(in_memory_chroma, mock_openai_client):
    """Test confidence threshold checking."""
    retriever = Retriever(
        chroma_client=in_memory_chroma,
        openai_client=mock_openai_client,
        embed_model="text-embedding-3-small"
    )

    # High-confidence chunks
    high_conf_chunks = [
        {"text": "test", "url": "test.com", "title": "Test", "score": 0.8}
    ]
    assert retriever.has_confident_match(high_conf_chunks) is True

    # Low-confidence chunks
    low_conf_chunks = [
        {"text": "test", "url": "test.com", "title": "Test", "score": 0.1}
    ]
    assert retriever.has_confident_match(low_conf_chunks) is False

    # Empty chunks
    assert retriever.has_confident_match([]) is False


def test_retriever_no_collection():
    """Test retriever behavior when collection doesn't exist."""
    client = chromadb.Client(ChromaSettings(
        is_persistent=False,
        allow_reset=True
    ))

    mock_openai = Mock()

    retriever = Retriever(
        chroma_client=client,
        openai_client=mock_openai,
        embed_model="text-embedding-3-small"
    )

    # Should return empty list when collection doesn't exist
    results = retriever.query("test question", k=5)
    assert results == []
