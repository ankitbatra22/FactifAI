'use client';

import { useState } from 'react';
import { ArrowTopRightOnSquareIcon } from '@heroicons/react/24/outline';
import type { SearchResponse, ResearchPaper } from '@/types/search';
import { useRouter } from 'next/navigation';

interface SearchResultsProps {
  results: SearchResponse;
}

export function SearchResults({ results }: SearchResultsProps) {
  const [activeTab, setActiveTab] = useState<'papers' | 'web'>('web');
  const router = useRouter();

  return (
    <div className="mt-8 space-y-6">
      {/* Query and Try Another Button */}
      <div className="flex justify-between items-center">
        <div className="space-y-2">
          <h1 className="text-2xl font-medium text-white/90">
            {/* Query would be passed as prop if needed */}
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

      {/* Tab Navigation */}
      <div className="flex gap-4 border-b border-gray-800">
        <button
          onClick={() => setActiveTab('web')}
          className={`pb-2 px-1 text-sm font-medium transition-colors relative
            ${activeTab === 'web' 
              ? 'text-white' 
              : 'text-gray-400 hover:text-gray-300'
            }`}
        >
          Web Summary
          {activeTab === 'web' && (
            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-500" />
          )}
        </button>
        <button
          onClick={() => setActiveTab('papers')}
          className={`pb-2 px-1 text-sm font-medium transition-colors relative
            ${activeTab === 'papers' 
              ? 'text-white' 
              : 'text-gray-400 hover:text-gray-300'
            }`}
        >
          Research Papers ({results.papers.length})
          {activeTab === 'papers' && (
            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-500" />
          )}
        </button>
      </div>

      {/* Content */}
      <div className="space-y-6">
        {activeTab === 'web' ? (
          <WebSummary summary={results.web_summary} />
        ) : (
          <PapersList papers={results.papers} />
        )}
      </div>
    </div>
  );
}

function WebSummary({ summary }: { summary: SearchResponse['web_summary'] }) {
  return (
    <div className="space-y-6">
      {/* Main Summary */}
      <div className="bg-[#2A2A2A] rounded-xl p-6">
        <p className="text-gray-300 leading-relaxed">
          {summary.summary}
        </p>
      </div>

      {/* Key Findings */}
      <div className="space-y-4">
        <h3 className="text-lg font-medium text-white">Key Findings</h3>
        <div className="grid gap-4">
          {summary.findings.map((finding, index) => (
            <div 
              key={index}
              className="bg-[#2A2A2A] rounded-lg p-4 hover:bg-[#333333] transition-colors"
            >
              <div className="flex justify-between gap-4">
                <p className="text-gray-300">{finding.text}</p>
                <a
                  href={finding.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex-shrink-0 text-blue-400 hover:text-blue-300 transition-colors"
                >
                  <ArrowTopRightOnSquareIcon className="w-5 h-5" />
                </a>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function PapersList({ papers }: { papers: ResearchPaper[] }) {
  return (
    <div className="grid gap-4">
      {papers.map((paper, index) => (
        <div 
          key={index}
          className="bg-[#2A2A2A] rounded-lg p-4 hover:bg-[#333333] transition-colors"
        >
          <div className="flex flex-col gap-2">
            <div className="flex justify-between items-start gap-4">
              <h3 className="text-white font-medium">
                {paper.title}
              </h3>
              <a
                href={paper.url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex-shrink-0 text-blue-400 hover:text-blue-300 transition-colors"
              >
                <ArrowTopRightOnSquareIcon className="w-5 h-5" />
              </a>
            </div>
            <p className="text-sm text-gray-400">
              {paper.summary}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}
