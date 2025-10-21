import { useState, useRef, useEffect } from 'react';
import { Message } from './Message';
import { askQuestion, type Source } from '../lib/api';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
}

export function Chat() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: 'assistant',
      content: 'Hello! I can answer questions about UW-Parkside. What would you like to know?',
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const question = input.trim();
    if (!question || isLoading) return;

    // Add user message
    const userMessage: ChatMessage = { role: 'user', content: question };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Get answer from API
      const response = await askQuestion(question);

      // Add assistant message
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.answer,
        sources: response.sources,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error asking question:', error);

      // Add error message
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error while processing your question. Please try again.',
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Messages area */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-3xl mx-auto">
          {messages.map((msg, index) => (
            <Message
              key={index}
              role={msg.role}
              content={msg.content}
              sources={msg.sources}
            />
          ))}

          {/* Loading indicator */}
          {isLoading && (
            <div className="flex justify-start mb-6">
              <div className="message-bubble message-assistant">
                <div className="flex items-center gap-2 text-gray-500">
                  <div className="flex gap-1">
                    <span className="w-2 h-2 bg-parkside-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                    <span className="w-2 h-2 bg-parkside-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                    <span className="w-2 h-2 bg-parkside-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                  </div>
                  <span className="text-sm">Thinking...</span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input area */}
      <div className="border-t border-gray-200 bg-white px-4 py-6">
        <form onSubmit={handleSubmit} className="max-w-3xl mx-auto">
          <div className="relative flex items-center">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a question about UW-Parkside..."
              disabled={isLoading}
              className="flex-1 px-5 py-3.5 pr-14 border border-gray-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-parkside-500 focus:border-transparent disabled:bg-gray-100 shadow-sm text-base"
              aria-label="Question input"
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="absolute right-2 p-2.5 bg-parkside-600 text-white rounded-xl hover:bg-parkside-700 focus:outline-none focus:ring-2 focus:ring-parkside-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              aria-label="Send question"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="currentColor"
                className="w-5 h-5"
              >
                <path d="M3.478 2.405a.75.75 0 00-.926.94l2.432 7.905H13.5a.75.75 0 010 1.5H4.984l-2.432 7.905a.75.75 0 00.926.94 60.519 60.519 0 0018.445-8.986.75.75 0 000-1.218A60.517 60.517 0 003.478 2.405z" />
              </svg>
            </button>
          </div>

          <p className="text-xs text-gray-500 mt-3 text-center">
            Ask about admissions, programs, campus life, or facilities
          </p>
        </form>
      </div>
    </div>
  );
}
