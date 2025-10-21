"""Tests for /ask endpoint."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.models import AskRequest


client = TestClient(app)


@pytest.fixture
def mock_retriever():
    """Mock retriever with sample chunks."""
    with patch("app.routers.ask.Retriever") as mock_class:
        mock_instance = Mock()

        # Mock high-confidence chunks
        mock_instance.query.return_value = [
            {
                "text": "UW-Parkside offers business, education, and science programs.",
                "url": "https://www.uwp.edu/academics",
                "title": "Academics",
                "score": 0.85
            },
            {
                "text": "The university has over 4,000 students enrolled.",
                "url": "https://www.uwp.edu/about",
                "title": "About",
                "score": 0.72
            }
        ]

        mock_instance.has_confident_match.return_value = True

        mock_class.return_value = mock_instance

        yield mock_instance


@pytest.fixture
def mock_openai():
    """Mock OpenAI client."""
    with patch("app.routers.ask.OpenAI") as mock_class:
        mock_instance = Mock()

        # Mock chat completion response
        mock_response = Mock()
        mock_response.choices = [
            Mock(message=Mock(content="UW-Parkside offers undergraduate and graduate programs in business, education, and sciences [1]. The university serves over 4,000 students [2]."))
        ]

        mock_instance.chat.completions.create.return_value = mock_response

        mock_class.return_value = mock_instance

        yield mock_instance


def test_ask_endpoint_success(mock_retriever, mock_openai):
    """Test successful question answering with citations."""
    response = client.post(
        "/ask",
        json={"question": "What programs does UW-Parkside offer?", "k": 5}
    )

    assert response.status_code == 200
    data = response.json()

    # Check response structure
    assert "answer" in data
    assert "sources" in data

    # Check answer contains citations
    assert "[1]" in data["answer"] or "[2]" in data["answer"]

    # Check sources are returned
    assert len(data["sources"]) > 0
    assert data["sources"][0]["url"] is not None


def test_ask_endpoint_low_confidence(mock_openai):
    """Test guardrail when no confident matches found."""
    with patch("app.routers.ask.Retriever") as mock_class:
        mock_instance = Mock()

        # Mock low-confidence chunks
        mock_instance.query.return_value = [
            {
                "text": "Some unrelated text",
                "url": "https://example.com",
                "title": "Example",
                "score": 0.1
            }
        ]

        mock_instance.has_confident_match.return_value = False
        mock_class.return_value = mock_instance

        response = client.post(
            "/ask",
            json={"question": "What is quantum physics?", "k": 5}
        )

        assert response.status_code == 200
        data = response.json()

        # Should return "don't know" message
        assert "don't have a reliable source" in data["answer"].lower()
        assert len(data["sources"]) == 0


def test_ask_endpoint_validation():
    """Test input validation."""
    # Empty question
    response = client.post(
        "/ask",
        json={"question": "", "k": 5}
    )
    assert response.status_code == 422  # Validation error

    # Invalid k value (too large)
    response = client.post(
        "/ask",
        json={"question": "Valid question", "k": 100}
    )
    assert response.status_code == 422  # Validation error

    # Invalid k value (negative)
    response = client.post(
        "/ask",
        json={"question": "Valid question", "k": -1}
    )
    assert response.status_code == 422  # Validation error


def test_ask_citation_format(mock_retriever, mock_openai):
    """Test that citations are properly formatted."""
    response = client.post(
        "/ask",
        json={"question": "Tell me about UW-Parkside", "k": 3}
    )

    assert response.status_code == 200
    data = response.json()

    # Verify OpenAI was called with correct system prompt
    mock_openai.chat.completions.create.assert_called_once()
    call_args = mock_openai.chat.completions.create.call_args

    # Check system prompt emphasizes citations
    messages = call_args.kwargs["messages"]
    system_message = next(m for m in messages if m["role"] == "system")
    assert "cite" in system_message["content"].lower()
    assert "[1]" in system_message["content"] or "bracketed" in system_message["content"].lower()
