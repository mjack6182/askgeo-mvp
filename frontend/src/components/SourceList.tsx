import { type Source } from '../lib/api';

interface SourceListProps {
  sources: Source[];
}

export function SourceList({ sources }: SourceListProps) {
  if (sources.length === 0) return null;

  return (
    <div className="mt-3 pt-3 border-t border-gray-200">
      <p className="text-xs font-medium text-gray-500 mb-2">Sources:</p>
      <div className="space-y-1">
        {sources.map((source, index) => {
          const url = new URL(source.url);
          const hostname = url.hostname.replace('www.', '');

          return (
            <a
              key={index}
              href={source.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-start gap-2 text-xs text-blue-600 hover:text-blue-800 hover:underline group"
            >
              <span className="citation-badge flex-shrink-0 group-hover:bg-blue-200">
                {index + 1}
              </span>
              <span className="flex-1 line-clamp-2">
                {source.title || 'Untitled'} <span className="text-gray-500">({hostname})</span>
              </span>
            </a>
          );
        })}
      </div>
    </div>
  );
}
