export function Footer() {
  return (
    <footer className="bg-white border-t border-gray-200 py-4">
      <div className="max-w-5xl mx-auto px-4 text-center text-sm text-gray-600">
        <p>
          Powered by{' '}
          <a
            href="https://openai.com"
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 hover:underline"
          >
            OpenAI
          </a>
          {' '}and{' '}
          <a
            href="https://www.trychroma.com"
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 hover:underline"
          >
            ChromaDB
          </a>
        </p>
        <p className="mt-1 text-xs">
          Information retrieved from the UW-Parkside website. Always verify important details.
        </p>
      </div>
    </footer>
  );
}
