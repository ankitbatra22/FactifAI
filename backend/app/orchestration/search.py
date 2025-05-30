from fastapi import HTTPException
from app.services.query.processor import QueryProcessor
from app.services.ingestion.pipeline import SearchPipeline
from app.services.search.google_search import GoogleSearchService, GoogleSearchResult
from app.services.search.serp_search import SerpSearchService, SerpSearchResponse
from app.services.llm.llm_service import LLMService
from app.schemas.search import SearchResponse, ResearchPaper
from app.schemas.research_summary import ResearchSummary
from app.config import settings
import asyncio
from typing import List, Union


class SearchOrchestrator:
    def __init__(self):
        self.query_processor = QueryProcessor()
        self.search_pipeline = SearchPipeline()
        self.search_service = (
            SerpSearchService() if settings.USE_SERP else GoogleSearchService()
        )
        self.llm_service = LLMService()

    async def search(self, query: str) -> SearchResponse:
        # 1. Process and validate query
        print(f"User entered query: {query}")
        processed = await self.query_processor.process_query(query)
        
        if not processed.processed_result.is_valid:
            return SearchResponse(
                is_valid=False,
                papers=[],
                web_summary=None,
            )

        # 2. Run academic search and web search in parallel
        async def academic_search():
            papers = await self.search_pipeline.search(processed.processed_result.academic_term)
            return papers

        async def web_search_and_summarize() -> ResearchSummary:
            web_results: List[Union[GoogleSearchResult, SerpSearchResponse]] = await self.search_service.search(query=query)
            summary: ResearchSummary = await self.llm_service.generate_summary(
                query=query,
                search_results=web_results
            )
            return summary

        # Execute searches in parallel
        academic_results, web_summary = await asyncio.gather(
            academic_search(),
            web_search_and_summarize()
        )

        # 3. Convert academic results to ResearchPaper objects
        papers = [
            ResearchPaper(
                title=paper['title'],
                summary=f"{paper['abstract'][:500]}...",  # Preview
                url=paper['url'],
                confidence=paper['score'],
                source=paper['source'],
                categories=paper['categories'],
                authors=paper['authors'],
                year=paper['year']
            )
            for paper in academic_results
        ]

        return SearchResponse(
            is_valid=True,
            papers=papers,
            web_summary=web_summary
        )