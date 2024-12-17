import pytest
import asyncio
from datetime import datetime
from unittest.mock import patch
from app.services.ingestion.sources.arxiv import ArxivConnector
from pytest_asyncio import fixture
from typing import List, Dict, Any


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
    results: List[Dict] = await arxiv_connector.fetch_papers("non-contrastive learning on graphs", max_results=5)

    assert len(results) > 0
    assert len(results) <= 5
    
    # Check structure of returned paper
    paper = results[0]
    # print(paper.keys())
    # print("Paper:")
    # print(paper)
    # print("Metadata:")
    # print(paper['metadata'])
    assert all(key in paper for key in ['id', 'title', 'content', 'url', 'source', 'metadata'])
    assert paper['source'] == 'arxiv'
    assert paper['id'].startswith('arxiv_')
    assert isinstance(paper['metadata'], dict)

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
    results = await arxiv_connector.fetch_papers("physics", max_results=max_results)
    assert len(results) <= max_results

@pytest.mark.asyncio
async def test_metadata_structure(arxiv_connector):
    """Test metadata structure of returned papers"""
    results: List[Dict] = await arxiv_connector.fetch_papers("physics", max_results=1)
    assert len(results) > 0
    
    metadata: Dict[str, Any] = results[0]['metadata']
    required_fields = {
        'authors', 'categories', 'published_date', 
        'updated_date', 'doi', 'primary_category'
    }
    
    assert all(field in metadata for field in required_fields)
    assert isinstance(metadata['authors'], list)
    assert isinstance(metadata['categories'], list)
    assert isinstance(metadata['published_date'], str)

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
    results: List[Dict] = await arxiv_connector.fetch_papers("@#$%^&*", max_results=5)
    assert isinstance(results, list)
    assert len(results) == 0

@pytest.mark.asyncio
async def test_concurrent_requests(arxiv_connector):
    """Test handling of concurrent requests"""
    queries = ["physics", "math", "computer science"]
    tasks: List[List[Dict]] = [arxiv_connector.fetch_papers(query, max_results=2) for query in queries]
    
    results = await asyncio.gather(*tasks)
    
    assert len(results) == 3
    for result in results:
        assert isinstance(result, list)
        assert len(result) <= 2
