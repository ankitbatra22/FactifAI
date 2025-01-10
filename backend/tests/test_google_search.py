import pytest
from app.services.search.google_search import GoogleSearchService, GoogleSearchResult
from typing import List
import re
from app.services.search.constants import EXCLUDED_DOMAINS

@pytest.mark.asyncio
async def test_google_search():
    """Test basic search functionality"""
    service = GoogleSearchService(num_results=5, debug=False)
    query = "Do cows form friendships scientific research"
    
    print(f"\nTesting Google Search...")
    print(f"Query: {query}")
    
    results = await service.search(query)
    
    # Basic validation
    assert results, "Should return some results"
    assert len(results) <= 5, "Should return requested number of results"
    assert all(isinstance(r, GoogleSearchResult) for r in results), "All results should be GoogleSearchResult objects"
    
    print("\nGoogle Search Results:")
    print("-" * 50)
    
    for result in results:
        print(f"\nTitle: {result.title}")
        print(f"Domain: {result.domain}")
        print(f"URL: {result.link}")
        print(f"Snippet: {result.snippet}")
        print(f"Source: {result.source}")
        print(f"Date: {result.date}")
        print("-" * 50)


@pytest.mark.asyncio
async def test_excluded_domains():
    """Test domain filtering"""
    service = GoogleSearchService(num_results=10)
    query = "reddit cows friendship quora"  # Query likely to return excluded domains
    
    results = await service.search(query)
    
    # Check that no results are from excluded domains
    for result in results:
        assert result.domain not in EXCLUDED_DOMAINS, f"Found excluded domain: {result.domain}"

@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling with invalid parameters"""
    service = GoogleSearchService()
    results = await service.search("")  # Empty query
    assert results == [], "Should handle empty query gracefully"

@pytest.mark.asyncio
async def test_result_relevance():
    """Test result relevance to query"""
    service = GoogleSearchService(num_results=5)
    query = "cow friendship scientific research"
    results = await service.search(query)
    
    # Check if results are relevant to the query
    query_terms = set(query.lower().split())
    for result in results:
        text = f"{result.title} {result.snippet}".lower()
        matching_terms = query_terms.intersection(set(text.split()))
        assert matching_terms, f"Result should contain at least one query term: {result.title}"