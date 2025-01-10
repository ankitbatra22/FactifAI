import React from 'react';
import { ResearchPaper } from '@/types/search';

interface PaperCardProps {
  paper: ResearchPaper;
}

// Helper function to decode HTML entities and clean up text
function cleanText(text: string): string {
  const textarea = document.createElement('textarea');
  textarea.innerHTML = text;
  return textarea.value
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&#8211;/g, '-')
    .replace(/&#8212;/g, '—')
    .replace(/&#8216;/g, "'")
    .replace(/&#8217;/g, "'")
    .replace(/&#8220;/g, '"')
    .replace(/&#8221;/g, '"');
}

export function PaperCard({ paper }: PaperCardProps) {
  return (
    <div className="bg-gray-800/50 rounded-lg p-4 hover:bg-gray-800/70 transition-colors">
      <div className="flex flex-col gap-3">
        {/* Title and Link */}
        <div className="flex justify-between items-start gap-4">
          <h3 className="text-white/90 font-medium">
            {cleanText(paper.title)}
          </h3>
          <a
            href={paper.url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex-shrink-0 text-blue-400 hover:text-blue-300 transition-colors"
          >
            <svg 
              className="w-5 h-5" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={2} 
                d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" 
              />
            </svg>
          </a>
        </div>

        {/* Year and Categories */}
        <div className="flex flex-wrap gap-2">
          {paper.year && (
            <span className="px-2 py-1 text-xs font-medium bg-gray-700/50 text-gray-300 rounded">
              {paper.year}
            </span>
          )}
          {paper.categories?.slice(0, 2).map((category, index) => (
            <span 
              key={index}
              className="px-2 py-1 text-xs font-medium bg-violet-500/10 text-violet-300 rounded"
            >
              {category}
            </span>
          ))}
        </div>

        {/* Authors with label */}
        {paper.authors && paper.authors.length > 0 && (
          <p className="text-sm">
            <span className="text-gray-300 font-medium">Authors: </span>
            <span className="text-gray-400">
              {paper.authors.slice(0, 3).join(', ')}
              {paper.authors.length > 3 && ' et al.'}
            </span>
          </p>
        )}

        {/* Summary */}
        {paper.summary && (
          <p className="text-sm text-gray-300 line-clamp-3">
            {paper.summary}
          </p>
        )}
      </div>
    </div>
  );
} 