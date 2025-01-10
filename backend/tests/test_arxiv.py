import pytest
import asyncio
from datetime import datetime
from unittest.mock import patch
from app.services.ingestion.sources.arxiv import ArxivConnector
from pytest_asyncio import fixture
from typing import List, Dict, Any
from app.schemas.paper import Paper, PaperMetadata

class MockSettings:
    ARXIV_RATE_LIMIT = 0.1  # Faster rate limit for testing

@fixture
async def arxiv_connector():
    """
    Fixture that provides an ArxivConnector instance with mock settings
    """
    with patch('app.services.ingestion.sources.arxiv.settings', MockSettings()):
        connector = ArxivConnector()
        return connector

@pytest.mark.asyncio
async def test_fetch_papers_basic(arxiv_connector):
    """Test basic paper fetching functionality"""

    query = "non-contrastive learning on graphs"
    results: List[Paper] = await arxiv_connector.fetch_papers(query, max_results=5)

    print(f"Found {len(results)} papers")
    for i, paper in enumerate(results, 1):
        print(f"\nPaper {i}:")
        print(f"Title: {paper.title}")
        if paper.metadata is not None:
            print(f"Abstract: {paper.metadata.abstract}")
            print(f"Authors: {paper.metadata.authors}")
            print(f"Year: {paper.metadata.year}")
            print(f"URL: {paper.url}")
        else:
            print("No metadata available for this paper")

    # assert len(results) > 0
    # assert len(results) <= 5
    
    # # Check structure of returned paper
    # paper = results[0]
    # # print(paper.keys())
    # # print("Paper:")
    # # print(paper)
    # # print("Metadata:")
    # # print(paper['metadata'])
    # assert all(key in paper for key in ['id', 'title', 'content', 'url', 'source', 'metadata'])
    # assert paper['source'] == 'arxiv'
    # assert paper['id'].startswith('arxiv_')
    # assert isinstance(paper['metadata'], dict)

@pytest.mark.asyncio
async def test_fetch_papers_empty_query(arxiv_connector):
    """Test behavior with empty query"""
    results = await arxiv_connector.fetch_papers("")
    assert isinstance(results, list)
    assert len(results) == 0

@pytest.mark.asyncio
async def test_fetch_papers_max_results(arxiv_connector):
    """Test max_results parameter"""
    max_results = 10
    papers: List[Paper] = await arxiv_connector.fetch_papers("physics", max_results=max_results)
    assert len(papers) <= max_results

@pytest.mark.asyncio
async def test_metadata_structure(arxiv_connector):
    """Test metadata structure of returned papers"""
    papers: List[Paper] = await arxiv_connector.fetch_papers("physics", max_results=1)
    assert len(papers) > 0

    paper = papers[0]
    assert paper.metadata is not None
    assert isinstance(paper.metadata, PaperMetadata)
    assert isinstance(paper.metadata.year, int)
    assert isinstance(paper.metadata.abstract, str)
    assert isinstance(paper.metadata.authors, list)
    assert isinstance(paper.metadata.categories, list)
    assert isinstance(paper.metadata.published_date, datetime)

@pytest.mark.asyncio
async def test_rate_limiting(arxiv_connector):
    """Test that rate limiting is respected"""
    start_time = datetime.now()
    
    # Fetch multiple results to trigger rate limiting
    results = await arxiv_connector.fetch_papers("physics", max_results=3)
    
    end_time = datetime.now()
    time_taken = (end_time - start_time).total_seconds()
    
    # Should take at least 0.2 seconds (3 results * 0.1 second mock rate limit)
    assert time_taken >= 0.2
    assert len(results) == 3

@pytest.mark.asyncio
async def test_error_handling(arxiv_connector):
    """Test error handling with invalid query"""
    results: List[Paper] = await arxiv_connector.fetch_papers("@#$%^&*", max_results=5)
    assert isinstance(results, list)
    assert len(results) == 0

@pytest.mark.asyncio
async def test_concurrent_requests(arxiv_connector):
    """Test handling of concurrent requests"""
    queries = ["physics", "math", "computer science"]
    tasks: List[List[Paper]] = [arxiv_connector.fetch_papers(query, max_results=2) for query in queries]
    
    results = await asyncio.gather(*tasks)
    
    assert len(results) == 3
    for result in results:
        assert isinstance(result, list)
        assert len(result) <= 2
