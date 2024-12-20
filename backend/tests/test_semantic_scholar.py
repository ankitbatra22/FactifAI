import pytest
from app.services.ingestion.sources.semantic_scholar import SemanticScholarConnector
from pytest_asyncio import fixture
from typing import List, Dict
from unittest.mock import patch

class MockSettings:
    SEMANTIC_SCHOLAR_API_KEY = "8kxH5DVIYTaE4X2naV3l83RYdf0bYxg7DSFdd7U3"
    SEMANTIC_SCHOLAR_RATE_LIMIT = 0.1  # Fast for testing

@fixture
async def semantic_scholar_connector():
    """Fixture that provides a SemanticScholarConnector instance"""
    with patch('app.services.ingestion.sources.semantic_scholar.settings', MockSettings()):
        connector = SemanticScholarConnector()
        return connector

@pytest.mark.asyncio
async def test_real_semantic_scholar_search(semantic_scholar_connector):
    """Test a real Semantic Scholar search"""
    results: List[Dict] = await semantic_scholar_connector.fetch_papers("Treatment for COVID-19", max_results=5)
    
    print("\nResults from Semantic Scholar:")
    for paper in results:
        print(f"\nTitle: {paper['title']}")
        print(f"Authors: {', '.join(author['name'] for author in paper['metadata']['authors'])}")
        print(f"Year: {paper['metadata']['year']}")
        print(f"Citations: {paper['metadata']['citation_count']}")
        print(f"URL: {paper['url']}")
        print(f"Abstract: {paper['metadata']['abstract'][:200]}...")
    
    assert len(results) > 0
    assert len(results) <= 5 