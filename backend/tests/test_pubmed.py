import pytest
from app.services.ingestion.sources.pubmed import PubMedConnector
from pytest_asyncio import fixture
from typing import List, Dict
from unittest.mock import patch

class MockSettings:
    PUBMED_EMAIL = "test@example.com"
    PUBMED_RATE_LIMIT = 0.34  # PubMed allows 3 requests/second

@fixture
async def pubmed_connector():
    """Fixture that provides a PubMedConnector instance"""
    with patch('app.services.ingestion.sources.pubmed.settings', MockSettings()):
        connector = PubMedConnector()
        return connector

@pytest.mark.asyncio
async def test_real_pubmed_search(pubmed_connector):
    """Test a real PubMed search"""
    results: List[Dict] = await pubmed_connector.fetch_papers("Treatment for COVID-19", max_results=5)
    
    print("\nResults from PubMed:")
    for paper in results:
        print(f"\nTitle: {paper['title']}")
        print(f"Authors: {', '.join(author['name'] for author in paper['metadata']['authors'])}")
        print(f"Journal: {paper['metadata']['journal']['title']}")
        print(f"URL: {paper['url']}")
        print(f"Abstract: {paper['metadata']['abstract'][:1000]}...")
    
    assert len(results) > 0
    assert len(results) <= 5