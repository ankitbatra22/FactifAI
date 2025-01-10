export interface ResearchPaper {
  title: string;
  summary: string;
  url: string;
  categories: string[];
  authors: string[];
  year: number;
  confidence: number;
  source: string;
}

export interface WebSummary {
  summary: string;
  findings: Array<{
    text: string;
    source_url: string;
  }>;
  error: string | null;
}

export interface SearchResponse {
  is_valid: boolean;
  papers: ResearchPaper[];
  web_summary: WebSummary;
}

export interface SearchQuery {
  query: string;
}