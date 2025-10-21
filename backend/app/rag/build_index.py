"""Build ChromaDB index from scraped documents."""
from typing import List, Dict, Tuple, Optional
import json
from datetime import datetime
from pathlib import Path
import tiktoken
from openai import OpenAI
import chromadb
from chromadb import PersistentClient


class IndexBuilder:
    """Build and populate ChromaDB vector index."""

    COLLECTION_NAME = "uwp"
    CHUNK_SIZE = 350  # tokens
    BATCH_SIZE = 100  # for embedding API calls

    def __init__(
        self,
        chroma_path: str = ".chroma",
        embed_model: str = "text-embedding-3-small",
        openai_api_key: str = None
    ):
        self.chroma_client = chromadb.PersistentClient(path=chroma_path)
        self.embed_model = embed_model
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def chunk_text(self, text: str, metadata: Dict) -> List[Tuple[str, dict, int]]:
        """Split text into chunks of ~CHUNK_SIZE tokens.

        Returns:
            List of (chunk_text, metadata, token_count) tuples
        """
        tokens = self.tokenizer.encode(text)
        chunks = []

        for i in range(0, len(tokens), self.CHUNK_SIZE):
            chunk_tokens = tokens[i:i + self.CHUNK_SIZE]
            chunk_text = self.tokenizer.decode(chunk_tokens)
            token_count = len(chunk_tokens)

            chunk_metadata = {
                **metadata,
                "token_count": token_count,
                "chunk_index": len(chunks)
            }

            chunks.append((chunk_text, chunk_metadata, token_count))

        return chunks

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a batch of texts using OpenAI API.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors
        """
        response = self.openai_client.embeddings.create(
            model=self.embed_model,
            input=texts
        )
        return [item.embedding for item in response.data]

    def build_index(self, jsonl_path: Path, reset: bool = True) -> dict:
        """Build ChromaDB index from JSONL file.

        Args:
            jsonl_path: Path to JSONL file with scraped docs
            reset: If True, delete existing collection and create new one

        Returns:
            Stats dict with counts and metadata
        """
        print(f"Building index from {jsonl_path}")

        # Load documents
        documents = []
        with open(jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                documents.append(json.loads(line))

        print(f"✓ Loaded {len(documents)} documents")

        # Get or create collection
        if reset:
            try:
                self.chroma_client.delete_collection(name=self.COLLECTION_NAME)
                print(f"✓ Deleted existing collection '{self.COLLECTION_NAME}'")
            except:
                pass

        collection = self.chroma_client.get_or_create_collection(
            name=self.COLLECTION_NAME,
            metadata={"description": "UW-Parkside website content"}
        )

        # Chunk all documents
        all_chunks = []
        for page_idx, doc in enumerate(documents):
            metadata = {
                "url": doc["url"],
                "title": doc.get("title") or "Untitled",  # Convert None to "Untitled"
                "page_index": page_idx
            }
            chunks = self.chunk_text(doc["text"], metadata)
            all_chunks.extend(chunks)

        print(f"✓ Created {len(all_chunks)} chunks from {len(documents)} documents")

        # Process in batches for embedding
        total_chunks = len(all_chunks)

        for batch_start in range(0, total_chunks, self.BATCH_SIZE):
            batch_end = min(batch_start + self.BATCH_SIZE, total_chunks)
            batch = all_chunks[batch_start:batch_end]

            print(f"Processing batch {batch_start//self.BATCH_SIZE + 1}: chunks {batch_start+1}-{batch_end}/{total_chunks}")

            # Extract texts and metadata
            texts = [chunk[0] for chunk in batch]
            metadatas = [chunk[1] for chunk in batch]

            # Generate embeddings
            embeddings = self.embed_texts(texts)

            # Generate IDs
            ids = []
            for chunk_meta in metadatas:
                page_idx = chunk_meta["page_index"]
                chunk_idx = chunk_meta["chunk_index"]
                ids.append(f"{page_idx}-{chunk_idx}")

            # Add to collection
            collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas
            )

        print(f"✓ Indexed {total_chunks} chunks")

        # Generate stats
        stats = {
            "created_at": datetime.now().isoformat(),
            "total_documents": len(documents),
            "total_chunks": total_chunks,
            "embed_model": self.embed_model,
            "collection_name": self.COLLECTION_NAME
        }

        return stats

    def save_stats(self, stats: Dict, output_path: Path) -> None:
        """Save indexing stats to JSON file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2)
        print(f"✓ Saved stats to {output_path}")


def main():
    """CLI entry point for building index."""
    import argparse
    from dotenv import load_dotenv
    import os

    load_dotenv()

    parser = argparse.ArgumentParser(description="Build ChromaDB index from scraped docs")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/uwp_docs.jsonl"),
        help="Input JSONL file path"
    )
    parser.add_argument(
        "--chroma-path",
        type=str,
        default=".chroma",
        help="ChromaDB persistent storage path"
    )
    parser.add_argument(
        "--stats-output",
        type=Path,
        default=Path("data/stats.json"),
        help="Output path for stats JSON"
    )
    parser.add_argument(
        "--no-reset",
        action="store_true",
        help="Don't delete existing collection"
    )

    args = parser.parse_args()

    # Get OpenAI API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        return

    embed_model = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")

    builder = IndexBuilder(
        chroma_path=args.chroma_path,
        embed_model=embed_model,
        openai_api_key=api_key
    )

    stats = builder.build_index(args.input, reset=not args.no_reset)
    builder.save_stats(stats, args.stats_output)

    print("\n✓ Index build complete!")


if __name__ == "__main__":
    main()
