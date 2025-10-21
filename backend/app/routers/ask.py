"""Ask endpoint for RAG question-answering."""
from fastapi import APIRouter, Depends, HTTPException
from openai import OpenAI
from chromadb import PersistentClient

from app.models import AskRequest, AskResponse, Source
from app.deps import get_settings, get_chroma_client
from app.settings import Settings
from app.rag.retriever import Retriever
from app.rag.prompts import SYSTEM_PROMPT, build_user_message

router = APIRouter()


@router.post("/ask", response_model=AskResponse)
async def ask_question(
    request: AskRequest,
    settings: Settings = Depends(get_settings),
    chroma_client: PersistentClient = Depends(get_chroma_client)
):
    """Answer a question using RAG.

    Args:
        request: Question and parameters

    Returns:
        Answer with citations and sources
    """
    # Initialize OpenAI client
    openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)

    # Initialize retriever
    retriever = Retriever(
        chroma_client=chroma_client,
        openai_client=openai_client,
        embed_model=settings.OPENAI_EMBED_MODEL
    )

    # Retrieve relevant chunks
    chunks = retriever.query(request.question, k=request.k)

    # Check if we have confident matches
    if not retriever.has_confident_match(chunks):
        return AskResponse(
            answer="I don't have a reliable source to answer that question. Please try rephrasing or ask about UW-Parkside programs, admissions, campus life, or academics.",
            sources=[]
        )

    # Build prompt
    chunks_with_meta = [(chunk["text"], {"url": chunk["url"], "title": chunk["title"]}) for chunk in chunks]
    user_message = build_user_message(request.question, chunks_with_meta)

    # Call OpenAI Chat Completions
    try:
        response = openai_client.chat.completions.create(
            model=settings.OPENAI_CHAT_MODEL,
            temperature=0.2,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ]
        )

        answer = response.choices[0].message.content

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")

    # Extract unique sources
    seen_urls = set()
    sources = []

    for chunk in chunks:
        if chunk["url"] not in seen_urls:
            seen_urls.add(chunk["url"])
            sources.append(Source(
                url=chunk["url"],
                title=chunk["title"]
            ))

    return AskResponse(
        answer=answer,
        sources=sources
    )
