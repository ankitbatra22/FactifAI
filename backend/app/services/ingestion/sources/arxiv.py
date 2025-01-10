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
            
            results = []
            try:
                async with asyncio.timeout(4):  # 4 second timeout
                    papers = list(search.results())  # This is the actual API call
                    print(f"ArxivConnector: Got {len(papers)} results")

                    for paper in papers:
                        try:
                            if len(results) >= max_results:
                                print(f"ArxivConnector: Reached max results limit of {max_results}")
                                break
                            
                            paper_model = Paper(
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
                            
                            results.append(paper_model)
                            
                        except Exception as e:
                            print(f"ArxivConnector: Error processing individual paper: {str(e)}")
                            continue
                    
                    print(f"ArxivConnector: Successfully processed {len(results)}/{len(papers)} papers")
                    return results
                
            except asyncio.TimeoutError:
                print(f"ArxivConnector: Timeout while fetching results. Processed {len(results)}/{len(papers) if 'papers' in locals() else '?'} papers before timeout")
                return results
            except Exception as e:
                print(f"ArxivConnector: Error processing results: {str(e)}")
                return results
            
        except Exception as e:
            print(f"ArxivConnector: Top-level error: {str(e)}")
            return []

    def _clean_text(self, text: str) -> str:
        """Clean and format text content"""
        if not text:
            return ""
        return " ".join(text.split())