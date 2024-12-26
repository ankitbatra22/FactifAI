'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export function SearchBar() {
  const [query, setQuery] = useState('');
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    
    router.push(`/results?q=${encodeURIComponent(query.trim())}`);
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      <form onSubmit={handleSubmit} className="relative group">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-violet-500 rounded-xl blur opacity-20 group-hover:opacity-30 transition-opacity" />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask anything..."
          className="w-full px-6 py-4 bg-[#1C1F26] rounded-xl
                   text-white placeholder-gray-400
                   border border-gray-800 focus:border-gray-700
                   outline-none transition-all
                   text-lg relative z-10
                   focus:ring-2 focus:ring-blue-500/20"
        />
        <div className="absolute right-4 top-1/2 -translate-y-1/2 flex items-center gap-3 z-10">
          <div className="flex items-center gap-2 text-gray-400">
            <span className="text-sm font-medium">Search</span>
            <kbd className="px-2 py-1 text-xs bg-gray-800 rounded-md border border-gray-700">⏎</kbd>
          </div>
        </div>
      </form>
    </div>
  );
}