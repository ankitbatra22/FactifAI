export interface ResearchPaper {
  title: string;
  summary: string;
  url: string;
  confidence?: number;
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
  papers: ResearchPaper[];
  web_summary: WebSummary;
}

export interface SearchQuery {
  query: string;
}