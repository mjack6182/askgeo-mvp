import { marked } from 'marked';
import { SourceList } from './SourceList';
import { type Source } from '../lib/api';

interface MessageProps {
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
}

export function Message({ role, content, sources = [] }: MessageProps) {
  const isUser = role === 'user';

  // Configure marked to be safer
  marked.setOptions({
    breaks: true,
    gfm: true,
  });

  const renderContent = () => {
    if (isUser) {
      return <p className="whitespace-pre-wrap leading-relaxed">{content}</p>;
    }

    // Render markdown for assistant messages
    const html = marked.parse(content) as string;

    return (
      <div
        className="prose prose-sm max-w-none prose-p:leading-relaxed"
        dangerouslySetInnerHTML={{ __html: html }}
      />
    );
  };

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-6`}>
      <div className={`message-bubble ${isUser ? 'message-user' : 'message-assistant'}`}>
        {renderContent()}
        {!isUser && sources.length > 0 && <SourceList sources={sources} />}
      </div>
    </div>
  );
}
