from typing import List, Dict
import arxiv
from datetime import datetime
from app.services.ingestion.sources.base import BaseSourceConnector
from app.config import settings

class ArxivConnector(BaseSourceConnector):
    def __init__(self):
        super().__init__()
        self.rate_limit = settings.ARXIV_RATE_LIMIT  # 3 seconds
        self.base_url = "http://export.arxiv.org/api/query"
        
    async def fetch_papers(self, query: str, max_results: int = 2000) -> List[Dict]:
        """
        Fetch papers from ArXiv based on query
        Args:
            query: Search query
            max_results: Maximum number of results (up to 2000 per request)
        """
        try:
            # Configure search client
            search = arxiv.Search(
                query=query,
                max_results=min(max_results, 2000),  # Respect ArXiv's limit
                sort_by=arxiv.SortCriterion.Relevance,  # Sort by relevance
                sort_order=arxiv.SortOrder.Descending
            )
            
            documents = []
            for paper in search.results():
                documents.append({
                    'id': f"arxiv_{paper.entry_id.split('/')[-1]}",
                    'title': paper.title,
                    'content': (
                        f"Abstract: {paper.summary}\n\n"
                        f"Authors: {', '.join(author.name for author in paper.authors)}\n"
                        f"Categories: {', '.join(paper.categories)}\n"
                        f"Published: {paper.published.strftime('%Y-%m-%d')}"
                    ),
                    'url': paper.entry_id,
                    'source': 'arxiv',
                    'metadata': {
                        'authors': [author.name for author in paper.authors],
                        'categories': paper.categories,
                        'published_date': paper.published.isoformat(),
                        'updated_date': paper.updated.isoformat(),
                        'doi': paper.doi,
                        'primary_category': paper.primary_category,
                        'comment': paper.comment,
                        'journal_ref': paper.journal_ref if hasattr(paper, 'journal_ref') else None
                    }
                })
                
                if len(documents) >= max_results:
                    break
                    
                # Respect rate limit between paper fetches
                await self.rate_limit_wait()
            
            print(f"ArXiv returned {len(documents)} results for query: {query}")
            return documents
            
        except Exception as e:
            print(f"Error fetching from ArXiv: {str(e)}")
            return []

    def _clean_text(self, text: str) -> str:
        """Clean and format text content"""
        if not text:
            return ""
        return " ".join(text.split())