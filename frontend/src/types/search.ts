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
    title: string;
    text: string;
    source_url: string;
    domain: string;
    source_name?: string;
    source_date?: string;
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