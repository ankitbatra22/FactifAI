import pytest
from app.services.search.serp_search import SerpSearchService, SerpSearchResult, SerpSearchResponse
import re

@pytest.mark.asyncio
async def test_serp_search():
    """Test basic search functionality with real API calls"""
    service = SerpSearchService(num_results=5)
    query = "can cows make friends"
    
    print(f"\nTesting SERP Search...")
    print(f"Query: {query}")
    
    response = await service.search(query)
    
    # Basic validation
    assert isinstance(response, SerpSearchResponse), "Should return a SerpSearchResponse object"
    assert response.results, "Should return some results"
    assert len(response.results) <= 5, "Should return requested number of results"
    assert all(isinstance(r, SerpSearchResult) for r in response.results), "All results should be SerpSearchResult objects"
    
    print("\nSERP Search Results:")
    print("-" * 50)
    
    for result in response.results:
        print(f"\nTitle: {result.title}")
        print(f"Domain: {result.domain}")
        print(f"URL: {result.link}")
        print(f"Snippet: {result.snippet}")
        if result.date:
            print(f"Date: {result.date}")
        print("-" * 50)

    # Check for SERP features if present
    if response.featured_snippet:
        print("\nFeatured Snippet:")
        print(response.featured_snippet)
        
    if response.ai_overview:
        print("\nAI Overview:")
        print(response.ai_overview)

@pytest.mark.asyncio
async def test_excluded_domains():
    """Test domain filtering with real API calls"""
    service = SerpSearchService(num_results=10)
    query = "reddit cows friendship quora"  # Query likely to return excluded domains
    
    response = await service.search(query)
    
    # Check that no results are from excluded domains
    for result in response.results:
        assert result.domain not in service.EXCLUDED_DOMAINS, f"Found excluded domain: {result.domain}"
        
    # Verify URL structure
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
    for result in response.results:
        assert url_pattern.match(result.link), f"Invalid URL format: {result.link}"

@pytest.mark.asyncio
async def test_special_characters():
    """Test handling of special characters in query"""
    service = SerpSearchService(num_results=3)
    query = "cow & friendship + research (2024)"
    response = await service.search(query)
    
    assert isinstance(response, SerpSearchResponse), "Should handle special characters gracefully"
    assert response.results, "Should return results even with special characters"

@pytest.mark.asyncio
async def test_result_structure():
    """Test the structure and content of search results"""
    service = SerpSearchService(num_results=3)
    response = await service.search("scientific studies on animal behavior")
    
    for result in response.results:
        # Check required fields
        assert result.title.strip(), "Title should not be empty"
        assert result.link.strip(), "Link should not be empty"
        assert result.snippet.strip(), "Snippet should not be empty"
        assert result.domain.strip(), "Domain should not be empty"
        
        # Check field types
        assert isinstance(result.title, str)
        assert isinstance(result.link, str)
        assert isinstance(result.snippet, str)
        assert isinstance(result.domain, str)
        assert isinstance(result.source, (str, type(None)))
        assert isinstance(result.date, (str, type(None)))