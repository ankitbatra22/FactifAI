from dataclasses import dataclass
from typing import List, Optional
import httpx
from bs4 import BeautifulSoup
import time
import random
from urllib.parse import urlparse
import asyncio
import logging
import json
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class GoogleSearchResult:
    """Individual search result with structured data"""
    title: str
    link: str
    snippet: str
    domain: str
    featured_snippet: Optional[str] = None

class GoogleSearchService:
    """Service to handle Google search operations"""
    
    BASE_URL = "https://www.google.com/search"
    
    # Bad domains to exclude
    EXCLUDED_DOMAINS = {
        'reddit.com', 'quora.com', 'pinterest.com', 
        'facebook.com', 'twitter.com', 'instagram.com',
        'tiktok.com', 'youtube.com', 'medium.com', 'linkedin.com',
        'towardsdatascience.com', 'wikihow.com', 'wikipedia.org',
        'yahoo.answers.com', 'answers.com', 'answers.yahoo.com',
        'buzzfeed.com', 'boredpanda.com', 'huffpost.com'
    }
    
    # Rotating set of common user agents
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15"
    ]
    
    # Add this near the top with other class variables
    EXCLUDED_URL_PATTERNS = [
        # Discussion/Forum indicators
        'forum', 'thread', 'discussion', 'community', 'comments',
        'board', 'topic', 'message', 'chat', 'conversation', 'talk',
        
        # Social/Q&A
        'reddit', 'quora', 'answers', 'ask', 'stackexchange',
        
        # User-generated content
        'blog', 'post', 'question', 'responses', 'replies'
    ]
    
    def __init__(self, 
                 language: str = "en", 
                 country: str = "US", 
                 location: str = "Austin,Texas", 
                 num_results: int = 10,
                 debug: bool = False):
        self.language = language
        self.country = country
        self.location = location
        self.num_results = num_results
        self.debug = debug
        
    def get_headers(self) -> dict:
        """Get headers with a random user agent"""
        return {
            "User-Agent": random.choice(self.USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": f"{self.language}-{self.country},{self.language};q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0"
        }
        
    def extract_domain(self, url: str) -> str:
        """Extract base domain from URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            return domain.replace('www.', '')
        except Exception as e:
            logger.error(f"Error extracting domain from {url}: {str(e)}")
            return ''

    def is_valid_source(self, url: str) -> bool:
        """Check if the source URL is valid (not in excluded list and no bad patterns)"""
        # Extract domain and check against excluded list
        domain = self.extract_domain(url)
        if domain in self.EXCLUDED_DOMAINS:
            return False
            
        # Check entire URL (including path) for excluded patterns
        url_lower = url.lower()
        if any(pattern in url_lower for pattern in self.EXCLUDED_URL_PATTERNS):
            logger.debug(f"Excluding URL due to pattern match: {url}")
            return False
            
        return True

    def save_debug_html(self, html: str, prefix: str = "google_response"):
        """Save HTML response for debugging"""
        if self.debug:
            timestamp = int(time.time())
            filename = f"debug_{prefix}_{timestamp}.html"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(html)
            logger.info(f"Saved debug HTML to {filename}")

    async def search(self, query: str) -> List[GoogleSearchResult]:
        """
        Perform Google search with filtering for reliable sources
        """
        try:
            # Add random delay between requests (2-5 seconds)
            await asyncio.sleep(random.uniform(2.1, 4.5))
            
            params = {
                'q': query,
                'hl': self.language,
                'gl': self.country,
                'num': self.num_results * 2,  # Request more to account for filtering
                'start': 0,
                'ie': 'utf8',
                'oe': 'utf8'
            }

            if self.location:
                params['uule'] = f"w+CAIQICI{self.location}"
                params['near'] = self.location

            logger.info(f"Sending request to: {self.BASE_URL}")
            logger.info(f"With params: {params}")
            
            async with httpx.AsyncClient(
                timeout=30.0,
                follow_redirects=True,
                verify=True
            ) as client:
                headers = self.get_headers()
                logger.info(f"Using User-Agent: {headers['User-Agent']}")
                
                response = await client.get(
                    self.BASE_URL,
                    headers=headers,
                    params=params
                )
                
                logger.info(f"Response status: {response.status_code}")
                logger.info(f"Response headers: {json.dumps(dict(response.headers), indent=2)}")
                
                if response.status_code != 200:
                    logger.error(f"Unexpected status code: {response.status_code}")
                    self.save_debug_html(response.text, "error_response")
                    return []
                
                html = response.text
                logger.info(f"Response length: {len(html)}")
                
                # Save response for debugging
                self.save_debug_html(html)
                
                if "Our systems have detected unusual traffic" in html:
                    logger.error("CAPTCHA detected!")
                    return []
                    
                # Check for other blocking patterns
                blocking_patterns = [
                    "detected unusual traffic",
                    "please show you're not a robot",
                    "automated requests"
                ]
                
                if any(pattern in html.lower() for pattern in blocking_patterns):
                    logger.error("Request appears to be blocked")
                    return []
                
                results = self._parse_results(html)
                if not results and self.debug:
                    logger.error("No results found in parsed response")
                
                return results
                
        except Exception as e:
            logger.error(f"Error performing search: {str(e)}", exc_info=True)
            return []

    def _parse_results(self, html: str) -> List[GoogleSearchResult]:
        """Parse and filter search results"""
        soup = BeautifulSoup(html, 'html.parser')
        search_results = []
        
        # First check if we can find any search result containers
        all_divs = soup.find_all('div')
        logger.info(f"Total div elements found: {len(all_divs)}")
        
        # Try different result container selectors
        selectors = [
            'div.g',  # Standard result container
            'div[class*="MjjYud"]',  # Alternative container
            'div[data-hveid]',  # Results with data attribute
            'div.rc',  # Legacy container
        ]
        
        results = []
        for selector in selectors:
            results = soup.select(selector)
            if results:
                logger.info(f"Found {len(results)} results using selector: {selector}")
                break
        
        if not results:
            logger.error("No result containers found with any selector")
            return []
            
        for result in results:
            try:
                # Debug print the result HTML
                if self.debug:
                    logger.debug(f"Processing result HTML: {result.prettify()}")
                
                # Extract title
                title_elem = result.select_one('h3')
                if not title_elem:
                    logger.debug("No title element found")
                    continue
                title = title_elem.get_text().strip()
                
                # Extract link
                link_elem = result.select_one('a')
                if not link_elem or not link_elem.get('href', '').startswith('http'):
                    logger.debug("No valid link element found")
                    continue
                link = link_elem['href']
                
                # Validate entire URL, not just domain
                if not self.is_valid_source(link):
                    logger.debug(f"Invalid source URL: {link}")
                    continue
                
                # Try different snippet selectors
                snippet = ''
                snippet_selectors = [
                    'div.VwiC3b',
                    'div[class*="lyLwlc"]',
                    'div[class*="snipp"]',
                    'div.s3v9rd',
                    'span.st'
                ]
                
                for snippet_selector in snippet_selectors:
                    snippet_elem = result.select_one(snippet_selector)
                    if snippet_elem:
                        snippet = snippet_elem.get_text().strip()
                        break
                        
                if not snippet:
                    logger.debug("No snippet found")
                    continue
                
                # Extract and validate domain
                domain = self.extract_domain(link)
                if not domain or not self.is_valid_source(domain):
                    logger.debug(f"Invalid domain: {domain}")
                    continue
                
                search_results.append(GoogleSearchResult(
                    title=title,
                    link=link,
                    snippet=snippet,
                    domain=domain,
                    featured_snippet=None  # We'll handle this separately
                ))
                
                if len(search_results) >= self.num_results:
                    break
                    
            except Exception as e:
                logger.error(f"Error parsing result: {str(e)}", exc_info=True)
                continue
        
        logger.info(f"Successfully parsed {len(search_results)} results")
        return search_results

    def _extract_featured_snippet(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract featured snippet if present"""
        selectors = [
            'div[data-tts="answers"]',
            'div.IZ6rdc',
            'div.V3FYCf',
            'div.xpdopen',
            'div[data-featured-snippet="true"]'
        ]
        
        for selector in selectors:
            featured = soup.select_one(selector)
            if featured:
                return featured.get_text().strip()
        
        return None