/**
 * API client for UW-Parkside RAG backend
 */

const API_BASE = '/api';

export interface Source {
  url: string;
  title: string | null;
}

export interface AskResponse {
  answer: string;
  sources: Source[];
}

export interface IngestStatus {
  status: 'idle' | 'running' | 'done' | 'error';
  pages_scraped: number;
  chunks_indexed: number;
  started_at: string | null;
  completed_at: string | null;
  error_message: string | null;
}

export interface HealthResponse {
  status: string;
  embed_model: string;
  chat_model: string;
  collection_exists: boolean;
  chunk_count: number;
}

/**
 * Ask a question to the RAG chatbot
 */
export async function askQuestion(question: string, k: number = 5): Promise<AskResponse> {
  const response = await fetch(`${API_BASE}/ask`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ question, k }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || 'Failed to get answer');
  }

  return response.json();
}

/**
 * Start ingestion process
 */
export async function startIngest(maxPages?: number): Promise<{ message: string; max_pages: number }> {
  const response = await fetch(`${API_BASE}/ingest/start`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ max_pages: maxPages }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || 'Failed to start ingestion');
  }

  return response.json();
}

/**
 * Get ingestion status
 */
export async function getIngestStatus(): Promise<IngestStatus> {
  const response = await fetch(`${API_BASE}/ingest/status`);

  if (!response.ok) {
    throw new Error('Failed to get ingest status');
  }

  return response.json();
}

/**
 * Get health status
 */
export async function getHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE}/health`);

  if (!response.ok) {
    throw new Error('Failed to get health status');
  }

  return response.json();
}
