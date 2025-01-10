import { useState, useEffect } from 'react';

const LOADING_MESSAGES = [
  "Indexing millions of research papers",
  "FactifAI is thinking...",
  "Checking the web for reliable sources",
  "Analyzing research papers",
  "Cross-referencing various findings",
  "FactifAI-ing your query",
  "Preparing your results!",
];

export function SearchLoading() {
  const [messageIndex, setMessageIndex] = useState(0);

  useEffect(() => {
    // Skip the first message in the rotation
    if (messageIndex === 0) {
      const initialDelay = setTimeout(() => {
        setMessageIndex(1);
      }, 10000);
      return () => clearTimeout(initialDelay);
    }

    // Rotate through other messages every 10 seconds
    const interval = setInterval(() => {
      setMessageIndex((current) => 
        current === LOADING_MESSAGES.length - 1 ? 1 : current + 1
      );
    }, 10000);

    return () => clearInterval(interval);
  }, [messageIndex]);

  return (
    <div className="text-center space-y-4 py-12">
      <div className="inline-block animate-spin rounded-full h-8 w-8 border-2 border-gray-200 border-t-blue-500 mb-4" />
      <div className="space-y-2">
        <p className="text-lg text-white/90 font-medium">
          {LOADING_MESSAGES[messageIndex]}
        </p>
        <p className="text-sm text-gray-400">
          Finding the most relevant and reliable sources to FactifAI your query
        </p>
      </div>
    </div>
  );
}