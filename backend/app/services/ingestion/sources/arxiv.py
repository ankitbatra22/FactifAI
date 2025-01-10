from typing import List, Dict
import arxiv
from datetime import datetime
from app.services.ingestion.sources.base import BaseSourceConnector
from app.config import settings
import asyncio
from app.schemas.paper import Paper, PaperMetadata

class ArxivConnector(BaseSourceConnector):
    def __init__(self):
        super().__init__()
        self.rate_limit = settings.ARXIV_RATE_LIMIT  # 3 seconds
        self.base_url = "http://export.arxiv.org/api/query"
        
    async def fetch_papers(self, query: str, max_results: int = 2000) -> List[Paper]:
        print(f"ArxivConnector: Fetching papers for query: {query}")
        try:
            if not query:
                return []
            
            # Rate limit the initial fetch only
            await self.rate_limit_wait()
            
            search = arxiv.Search(
                query=query,
                max_results=min(max_results, 30),
                sort_by=arxiv.SortCriterion.Relevance,
                sort_order=arxiv.SortOrder.Descending
            )
            
            try:
                async with asyncio.timeout(4):
                    papers = list(search.results())
                    print(f"ArxivConnector: Got {len(papers)} results")
                    
                    results = [
                        Paper(
                            title=paper.title,
                            url=paper.entry_id,
                            metadata=PaperMetadata(
                                authors=[author.name for author in paper.authors],
                                year=paper.published.year,
                                published_date=paper.published,
                                abstract=paper.summary,
                                categories=paper.categories
                            )
                        )
                        for paper in papers[:max_results]
                    ]
                    
                    print(f"ArxivConnector: Successfully processed {len(results)} papers")
                    return results
                
            except asyncio.TimeoutError:
                print(f"ArxivConnector: Timeout while fetching results")
                return []
            except Exception as e:
                print(f"ArxivConnector: Error processing results: {str(e)}")
                return []
            
        except Exception as e:
            print(f"ArxivConnector: Top-level error: {str(e)}")
            return []

    def _clean_text(self, text: str) -> str:
        """Clean and format text content"""
        if not text:
            return ""
        return " ".join(text.split())