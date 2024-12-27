'use client';

import { useSearchParams, useRouter } from 'next/navigation';
import { useState, useEffect } from 'react';
import { Header } from '@/components/layout/Header';
import { SearchLoading } from '../../components/search/SearchLoading';
import { searchPapers } from '@/lib/api';
import type { SearchResponse } from '@/types/search';

const CACHE_KEY_PREFIX = 'search_results_';

export default function ResultsPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const query = searchParams.get('q');
  const [results, setResults] = useState<SearchResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  // Add mounted state to prevent hydration mismatch
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    const fetchResults = async () => {
      if (!query) return;

      const cacheKey = CACHE_KEY_PREFIX + query;
      
      try {
        setIsLoading(true);
        const data = await searchPapers(query);
        
        // Check if query was invalid according to the LLM validator
        if (!data.is_valid) {
          setError('Please enter a valid query. For example: "Can Cows Make Friends?"');
          setResults(null);
          return;
        }

        setResults(data);
        setError(null);
        localStorage.setItem(cacheKey, JSON.stringify(data));
      } catch (err) {
        setError('An error occurred while searching. Please try again.');
        setResults(null);
      } finally {
        setIsLoading(false);
      }
    };

    if (mounted) {
      fetchResults();
    }
  }, [query, mounted]);

  useEffect(() => {
    if (!mounted) return; // Skip cache cleanup until mounted

    const clearOldCache = () => {
      const keys = Object.keys(localStorage);
      const searchKeys = keys.filter(key => key.startsWith(CACHE_KEY_PREFIX));
      
      // Keep only the last 10 searches
      if (searchKeys.length > 10) {
        searchKeys
          .slice(0, searchKeys.length - 10)
          .forEach(key => localStorage.removeItem(key));
      }
    };

    clearOldCache();
  }, [mounted]);

  // Don't render anything until after hydration
  if (!mounted) return null;
  if (!query) return null;

  return (
    <div className="min-h-screen bg-[#0D1117] text-white">
      <Header />
      
      <main className="container mx-auto px-4 py-16 max-w-4xl">
        {isLoading ? (
          <SearchLoading />
        ) : error ? (
          <div className="text-center">
            <p className="text-red-400">{error}</p>
            <button
              onClick={() => router.push('/')}
              className="mt-4 px-4 py-2 text-sm font-medium text-gray-300 
                       bg-[#2A2A2A] rounded-lg hover:bg-[#333333] 
                       transition-colors flex items-center gap-2 mx-auto"
            >
              <span>Try Another Search</span>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                      d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </button>
          </div>
        ) : results ? (
          <div className="space-y-12">
            {/* Query and Try Another Button */}
            <div className="flex justify-between items-center">
              <div className="space-y-2">
                <h1 className="text-2xl font-medium text-white/90">
                  {query}
                </h1>
                <p className="text-sm text-gray-400">
                  Research-backed answer
                </p>
              </div>
              <button
                onClick={() => router.push('/')}
                className="px-4 py-2 text-sm font-medium text-gray-300 
                           bg-[#2A2A2A] rounded-lg
                           hover:bg-[#333333] transition-colors
                           flex items-center gap-2"
              >
                <span>Try Another Search</span>
                <svg 
                  className="w-4 h-4" 
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path 
                    strokeLinecap="round" 
                    strokeLinejoin="round" 
                    strokeWidth={2} 
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" 
                  />
                </svg>
              </button>
            </div>

            {/* Web Summary */}
            <div className="space-y-8">
              <div className="prose prose-invert max-w-none">
                <p className="text-lg leading-relaxed text-gray-200">
                  {results.web_summary.summary}
                </p>
              </div>

              {/* Key Findings with Citations */}
              <div className="space-y-4">
                <h2 className="text-lg font-medium text-white/90">Key Findings</h2>
                <div className="grid gap-4">
                  {results.web_summary.findings.slice(0, 3).map((finding, index) => (
                    <div 
                      key={index}
                      className="bg-gray-800/50 rounded-lg p-4 hover:bg-gray-800/70 transition-colors"
                    >
                      <div className="flex justify-between gap-4">
                        <div className="space-y-2">
                          <p className="text-gray-200">{finding.text}</p>
                          <p className="text-sm text-gray-400">
                            Source: {new URL(finding.source_url).hostname}
                          </p>
                        </div>
                        <a
                          href={finding.source_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex-shrink-0 text-blue-400 hover:text-blue-300 transition-colors"
                        >
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                          </svg>
                        </a>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Research Papers */}
              <div className="space-y-4">
                <h2 className="text-lg font-medium text-white/90">Relevant Research Papers</h2>
                <div className="grid gap-4">
                  {results.papers.map((paper, index) => (
                    <div 
                      key={index}
                      className="bg-gray-800/50 rounded-lg p-4 hover:bg-gray-800/70 transition-colors"
                    >
                      <div className="flex flex-col gap-2">
                        <div className="flex justify-between items-start gap-4">
                          <h3 className="text-white/90 font-medium">
                            {paper.title}
                          </h3>
                          <a
                            href={paper.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex-shrink-0 text-blue-400 hover:text-blue-300 transition-colors"
                          >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                            </svg>
                          </a>
                        </div>
                        <p className="text-sm text-gray-400">
                          {paper.summary}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ) : null}
      </main>
    </div>
  );
}