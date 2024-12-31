from dataclasses import dataclass
from typing import List, Optional, Dict
from serpapi import GoogleSearch
from urllib.parse import urlparse
import logging
from app.config import settings
from app.services.search.constants import EXCLUDED_DOMAINS, EXCLUDED_URL_PATTERNS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SerpSearchResult:
    """Individual search result with structured data"""
    title: str
    link: str
    snippet: str
    domain: str
    source: Optional[str] = None
    date: Optional[str] = None

@dataclass
class SerpSearchResponse:
    """Container for search results and metadata"""
    results: List[SerpSearchResult]
    featured_snippet: Optional[str] = None
    ai_overview: Optional[str] = None
    answer_box: Optional[dict] = None

    def __iter__(self):
        """Make results iterable for LLM service"""
        return iter(self.results)

class SerpSearchService:
    """Service to handle Google search operations via SerpAPI"""
    
    def __init__(self, num_results: int = 8):
        self.num_results = num_results

    def extract_domain(self, url: str) -> str:
        """Extract base domain from URL"""
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower().replace('www.', '')
        except Exception as e:
            logger.error(f"Error extracting domain from {url}: {str(e)}")
            return ''

    def is_valid_source(self, url: str) -> bool:
        """Check if the source URL is valid (not in excluded list and no bad patterns)"""
        # Extract domain and check against excluded list
        domain = self.extract_domain(url)
        if domain in EXCLUDED_DOMAINS:
            return False
            
        # Check entire URL (including path) for excluded patterns
        url_lower = url.lower()
        if any(pattern in url_lower for pattern in EXCLUDED_URL_PATTERNS):
            logger.debug(f"Excluding URL due to pattern match: {url}")
            return False
            
        return True

    async def search(self, query: str) -> SerpSearchResponse:
        """Perform Google search using SerpAPI"""
        try:
            params = {
                "api_key": settings.SERP_API_KEY,
                "q": query,
            }

            search = GoogleSearch(params)
            data = search.get_dict()

            # Extract global features
            featured_snippet = None
            if 'answer_box' in data:
                featured_snippet = data['answer_box'].get('snippet')
                
            # Only set ai_overview if it contains actual content (text_blocks)
            ai_overview = None
            if 'ai_overview' in data and isinstance(data['ai_overview'], dict):
                overview = data['ai_overview']
                if 'text_blocks' in overview and overview['text_blocks']:
                    ai_overview = overview

            # Get results and filter by domain and URL patterns
            results = []
            for result in data.get('organic_results', []):
                link = result.get('link', '')
                if self.is_valid_source(link):  # Using the new validation method
                    domain = self.extract_domain(link)
                    results.append(SerpSearchResult(
                        title=result.get('title', ''),
                        link=link,
                        snippet=result.get('snippet', ''),
                        domain=domain,
                        source=result.get('source'),
                        date=result.get('date')
                    ))
                    if len(results) >= self.num_results:
                        break

            return SerpSearchResponse(
                results=results,
                featured_snippet=featured_snippet,
                ai_overview=ai_overview['text_blocks'][0]['snippet'] if ai_overview else None,
                answer_box=data.get('answer_box')
            )

        except Exception as e:
            logger.error(f"Error performing search: {str(e)}", exc_info=True)
            return SerpSearchResponse(results=[]) 