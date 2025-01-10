'use client';

import { useSearchParams, useRouter } from 'next/navigation';
import { useState, useEffect, Suspense } from 'react';
import { Header } from '@/components/layout/Header';
import { SearchLoading } from '../../components/search/SearchLoading';
import { searchPapers } from '@/lib/api';
import type { SearchResponse } from '@/types/search';
import { PaperCard } from '@/components/PaperCard';
import { FindingCard } from '@/components/FindingCard';

export const dynamic = 'force-dynamic';
const CACHE_KEY_PREFIX = 'search_results_';

// Create a wrapped component that uses useSearchParams
function ResultsContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const query = searchParams.get('q');
  const [results, setResults] = useState<SearchResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isInitialLoad, setIsInitialLoad] = useState(true);

  // Handle initial load separately
  useEffect(() => {
    if (!query) return;

    const cacheKey = CACHE_KEY_PREFIX + query;
    const cached = localStorage.getItem(cacheKey);
    
    if (cached) {
      try {
        const parsedData = JSON.parse(cached) as SearchResponse;
        setResults(parsedData);
        setIsLoading(false);
      } catch {
        localStorage.removeItem(cacheKey);
      }
    }
    
    setIsInitialLoad(false);
  }, [query]);

  // Handle subsequent data fetching
  useEffect(() => {
    if (!query || isInitialLoad) return;

    const fetchResults = async () => {
      const cacheKey = CACHE_KEY_PREFIX + query;
      
      if (!results) {
        setIsLoading(true);
        try {
          const data = await searchPapers(query);
          
          if (!data.is_valid) {
            setError('Please enter a valid research question. For example: "Can Cows Make Friends?"');
            setResults(null);
          } else {
            setResults(data);
            setError(null);
            localStorage.setItem(cacheKey, JSON.stringify(data));
          }
        } catch (error: unknown) {
          console.error('Search error:', error);
          if (typeof error === 'object' && error !== null && 'status' in error && error.status === 429) {
            // @ts-expect-error Custom error type from API
            setError(error.message);
          } else {
            setError('An error occurred while searching. Please try again.');
          }
          setResults(null);
        } finally {
          setIsLoading(false);
        }
      }
    };

    fetchResults();
  }, [query, isInitialLoad, results]);

  if (!query) return null;

  return (
    <div className="min-h-screen bg-[#0D1117] text-white">
      <Header />
      <main className="container mx-auto px-4 pt-32 pb-16 max-w-4xl">
        {isLoading ? (
          <SearchLoading />
        ) : error ? (
          <div className="text-center space-y-6">
            <p className="text-lg text-gray-200 bg-red-500/10 border border-red-500/20 rounded-lg px-6 py-4">
              {error}
            </p>
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
            {/* Header section */}
            <div className="flex items-start justify-between border-b border-gray-800 pb-6">
              <div className="space-y-1">
                <h1 className="text-3xl font-medium text-white/90">
                  {query}
                </h1>
              </div>
              <button
                onClick={() => router.push('/')}
                className="flex items-center gap-2 px-4 py-2 text-sm font-medium 
                         text-gray-300 bg-[#2A2A2A] rounded-lg hover:bg-[#333333] 
                         transition-colors flex-shrink-0"
              >
                <span>New Search</span>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                        d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </button>
            </div>

            {/* Web Summary with enhanced header */}
            <div className="space-y-8">
              <div className="space-y-4">
                <div className="border-l-4 border-blue-500 pl-4">
                  <h2 className="text-lg font-semibold text-white/90 tracking-wide">
                    FactifAI&apos;s Research-Backed Answer:
                  </h2>
                </div>
                <div className="prose prose-invert max-w-none">
                  <p className="text-lg leading-relaxed text-gray-200">
                    {results.web_summary.summary}
                  </p>
                </div>
              </div>

              {/* Research Papers */}
              <div className="space-y-4 mb-8">
                <h2 className="text-lg font-medium text-white/90">
                  Relevant Research Papers
                </h2>
                <div className="grid gap-4">
                  {results.papers.map((paper, index) => (
                    <PaperCard key={index} paper={paper} />
                  ))}
                </div>
              </div>

              {/* Key Findings with Citations */}
              <div className="space-y-4">
                <h2 className="text-lg font-medium text-white/90">
                  Reliable Web Search Findings
                </h2>
                <div className="grid gap-4">
                  {results.web_summary.findings.slice(0, 3).map((finding, index) => (
                    <FindingCard 
                      key={index}
                      title={finding.title}
                      text={finding.text}
                      source_url={finding.source_url}
                      domain={finding.domain}
                      source_name={finding.source_name}
                      source_date={finding.source_date}
                    />
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

// Main page component with Suspense boundary
export default function ResultsPage() {
  return (
    <Suspense fallback={<SearchLoading />}>
      <ResultsContent />
    </Suspense>
  );
}