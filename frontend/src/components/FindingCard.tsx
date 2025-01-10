import React from 'react';

interface FindingProps {
  title: string;
  text: string;
  source_url: string;
  domain: string;
  source_name?: string;
  source_date?: string;
}

export function FindingCard({ title, text, source_url, source_name, source_date }: FindingProps) {
  return (
    <div className="bg-gray-800/50 rounded-lg p-4 hover:bg-gray-800/70 transition-colors">
      <div className="flex flex-col gap-3">
        {/* Title and Link */}
        <div className="flex justify-between items-start gap-4">
          <h3 className="text-white/90 font-medium">
            {title}
          </h3>
          <a
            href={source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex-shrink-0 text-blue-400 hover:text-blue-300 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                    d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
          </a>
        </div>

        {/* Source Badges */}
        <div className="flex flex-wrap gap-2">
          {source_date && (
            <span className="px-2 py-1 text-xs font-medium bg-gray-700/50 text-gray-300 rounded">
              {source_date}
            </span>
          )}
          {source_name && (
            <span className="px-2 py-1 text-xs font-medium bg-blue-500/10 text-blue-300 rounded">
              {source_name}
            </span>
          )}
        </div>

        {/* Main Text */}
        <p className="text-sm text-gray-300">
          {text}
        </p>
      </div>
    </div>
  );
} 