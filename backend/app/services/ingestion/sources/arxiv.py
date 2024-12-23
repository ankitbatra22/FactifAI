from typing import List, Dict
import arxiv
from datetime import datetime
from app.services.ingestion.sources.base import BaseSourceConnector
from app.config import settings
import asyncio

class ArxivConnector(BaseSourceConnector):
    def __init__(self):
        super().__init__()
        self.rate_limit = settings.ARXIV_RATE_LIMIT  # 3 seconds
        self.base_url = "http://export.arxiv.org/api/query"
        
    async def fetch_papers(self, query: str, max_results: int = 2000) -> List[Dict]:
        print(f"ArxivConnector: Starting fetch for query: {query}")
        try:
            print("ArxivConnector: Configuring search client...")
            search = arxiv.Search(
                query=query,
                max_results=min(max_results, 20),  # Start with just 20 results for speed
                sort_by=arxiv.SortCriterion.Relevance,
                sort_order=arxiv.SortOrder.Descending
            )
            
            print("ArxivConnector: Starting to fetch results...")
            documents = []
            
            try:
                async with asyncio.timeout(5):  # Quick 5-second timeout for initial results
                    for paper in search.results():
                        print(f"ArxivConnector: Processing paper {len(documents) + 1}")
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
                            'source': 'arxiv'
                        })
                        
                        if len(documents) >= 20:  # Fast return with initial results
                            break
                            
                        await self.rate_limit_wait()
            
            except asyncio.TimeoutError:
                print("ArxivConnector: Initial fetch timed out after 5 seconds")
            
            print(f"ArxivConnector: Completed with {len(documents)} documents")
            return documents
            
        except Exception as e:
            print(f"ArxivConnector Error: {str(e)}")
            print(f"ArxivConnector Error type: {type(e)}")
            return []

    def _clean_text(self, text: str) -> str:
        """Clean and format text content"""
        if not text:
            return ""
        return " ".join(text.split())