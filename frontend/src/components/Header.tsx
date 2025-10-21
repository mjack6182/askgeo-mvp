import { useEffect, useState } from 'react';
import { getIngestStatus, startIngest, type IngestStatus } from '../lib/api';
import verticalLogo from '../assets/vertical-logo.png';

export function Header() {
  const [ingestStatus, setIngestStatus] = useState<IngestStatus | null>(null);
  const [showReindexModal, setShowReindexModal] = useState(false);
  const [isReindexing, setIsReindexing] = useState(false);

  useEffect(() => {
    // Initial load
    loadIngestStatus();

    // Poll every 5 seconds if ingestion is running
    const interval = setInterval(() => {
      if (ingestStatus?.status === 'running') {
        loadIngestStatus();
      }
    }, 5000);

    return () => clearInterval(interval);
  }, [ingestStatus?.status]);

  const loadIngestStatus = async () => {
    try {
      const status = await getIngestStatus();
      setIngestStatus(status);
    } catch (error) {
      console.error('Failed to load ingest status:', error);
    }
  };

  const handleReindex = async () => {
    setIsReindexing(true);
    try {
      await startIngest();
      setShowReindexModal(false);
      // Reload status
      await loadIngestStatus();
    } catch (error) {
      console.error('Failed to start reindexing:', error);
      alert('Failed to start reindexing. Check console for details.');
    } finally {
      setIsReindexing(false);
    }
  };

  const getStatusBadge = () => {
    if (!ingestStatus) return null;

    const badges = {
      idle: (
        <span className="px-2 py-1 text-xs font-medium rounded-full bg-gray-200 text-gray-700">
          Ready
        </span>
      ),
      running: (
        <span className="px-2 py-1 text-xs font-medium rounded-full bg-parkside-100 text-parkside-700 flex items-center gap-1">
          <span className="inline-block w-2 h-2 bg-parkside-600 rounded-full animate-pulse"></span>
          Indexing...
        </span>
      ),
      done: (
        <span className="px-2 py-1 text-xs font-medium rounded-full bg-parkside-100 text-parkside-700">
          ✓ Indexed
        </span>
      ),
      error: (
        <span className="px-2 py-1 text-xs font-medium rounded-full bg-red-100 text-red-700">
          ✗ Error
        </span>
      ),
    };

    return badges[ingestStatus.status];
  };

  return (
    <>
      <header className="bg-parkside-600 border-b border-parkside-700 sticky top-0 z-10 shadow-sm">
        <div className="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <img
              src={verticalLogo}
              alt="UW-Parkside Logo"
              className="h-16 w-auto"
            />
            <div>
              <h1 className="text-xl font-bold text-white">Ask Geo</h1>
              <p className="text-sm text-parkside-100">Ask questions about the university</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {getStatusBadge()}

            <button
              onClick={() => setShowReindexModal(true)}
              disabled={ingestStatus?.status === 'running'}
              className="btn-secondary text-sm"
            >
              Re-index Data
            </button>
          </div>
        </div>
      </header>

      {/* Reindex Modal */}
      {showReindexModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <h2 className="text-lg font-bold mb-2">Re-index UW-Parkside Data?</h2>
            <p className="text-gray-600 mb-4">
              This will scrape the UW-Parkside website and rebuild the search index.
              This process may take several minutes.
            </p>

            {ingestStatus && ingestStatus.chunks_indexed > 0 && (
              <div className="bg-gray-50 rounded p-3 mb-4 text-sm">
                <p className="text-gray-700">
                  Current index: <strong>{ingestStatus.chunks_indexed}</strong> chunks
                  from <strong>{ingestStatus.pages_scraped}</strong> pages
                </p>
              </div>
            )}

            <div className="flex gap-2 justify-end">
              <button
                onClick={() => setShowReindexModal(false)}
                disabled={isReindexing}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={handleReindex}
                disabled={isReindexing}
                className="btn-primary"
              >
                {isReindexing ? 'Starting...' : 'Start Re-index'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
