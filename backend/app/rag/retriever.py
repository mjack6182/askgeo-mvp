"""Retrieval functions for querying ChromaDB."""
from typing import List, Dict, Tuple, Optional
from chromadb import PersistentClient
from openai import OpenAI


class Retriever:
    """Retrieve relevant document chunks from ChromaDB."""

    COLLECTION_NAME = "uwp"
    SIMILARITY_THRESHOLD = 0.2  # Minimum similarity score

    def __init__(
        self,
        chroma_client: PersistentClient,
        openai_client: OpenAI,
        embed_model: str = "text-embedding-3-small"
    ):
        self.chroma_client = chroma_client
        self.openai_client = openai_client
        self.embed_model = embed_model

        # Get collection
        try:
            self.collection = chroma_client.get_collection(name=self.COLLECTION_NAME)
        except Exception:
            # Collection doesn't exist yet
            self.collection = None

    def embed_query(self, query: str) -> List[float]:
        """Generate embedding for query text."""
        response = self.openai_client.embeddings.create(
            model=self.embed_model,
            input=[query]
        )
        return response.data[0].embedding

    def query(self, question: str, k: int = 5) -> List[dict]:
        """Retrieve top-k relevant chunks for a question.

        Args:
            question: User's question
            k: Number of chunks to retrieve

        Returns:
            List of dicts with keys: text, url, title, score
        """
        if not self.collection:
            return []

        # Generate query embedding
        query_embedding = self.embed_query(question)

        # Query ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            include=["documents", "metadatas", "distances"]
        )

        # Format results
        chunks = []

        if not results["documents"] or not results["documents"][0]:
            return []

        for i, doc in enumerate(results["documents"][0]):
            metadata = results["metadatas"][0][i]
            distance = results["distances"][0][i]

            # Convert distance to similarity score (ChromaDB uses L2 distance)
            # For normalized embeddings: similarity ≈ 1 - (distance² / 4)
            similarity = max(0, 1 - (distance ** 2) / 4)

            chunks.append({
                "text": doc,
                "url": metadata.get("url", ""),
                "title": metadata.get("title", "Untitled"),
                "score": similarity
            })

        return chunks

    def has_confident_match(self, chunks: List[dict]) -> bool:
        """Check if any retrieved chunk meets the confidence threshold."""
        if not chunks:
            return False
        return any(chunk["score"] >= self.SIMILARITY_THRESHOLD for chunk in chunks)
