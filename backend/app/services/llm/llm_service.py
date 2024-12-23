from typing import List, Optional
from openai import AsyncOpenAI
from app.services.search.google_search import GoogleSearchResult
from app.config import settings
from app.schemas.research_summary import ResearchSummary

class LLMService:
    """Service to generate research summaries from search results"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
    async def generate_summary(
        self, 
        query: str, 
        search_results: List[GoogleSearchResult]
    ) -> ResearchSummary:
        """Generate a research summary from search results"""
        
        if not search_results:
            return ResearchSummary(
                summary="No search results available.",
                findings=[],
                error="No search results to analyze"
            )
        
        context = self._prepare_context(search_results)
        
        messages = [
            {"role": "system", "content": """
            You are a factual research assistant that provides accurate, well-sourced information.
            Analyze the provided search results and generate a structured response that:
            1. Summarizes the key findings
            2. Lists specific claims with their sources
            
            Focus on verifiable facts from reputable sources.
            """},
            {"role": "user", "content": f"""
            Research Question: {query}
            
            Available Sources:
            {context}
            
            Generate a research summary with key findings and their sources.
            """}
        ]
        
        try:
            completion = await self.client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=messages,
                response_format=ResearchSummary,
            )
            
            return completion.choices[0].message.parsed
            
        except Exception as e:
            print(f"Error parsing LLM response: {e}")
            return ResearchSummary(
                summary="Error generating summary",
                findings=[],
                error=str(e)
            )
    
    def _prepare_context(self, results: List[GoogleSearchResult]) -> str:
        """Format search results as context for the LLM"""
        if not results:
            return "No search results available."
            
        context = []
        for i, result in enumerate(results, 1):
            context.append(f"""
            Source {i}:
            Title: {result.title}
            URL: {result.link}
            Domain: {result.domain}
            Content: {result.snippet}
            """)
        return "\n".join(context) 