import pytest
from app.services.ingestion.sources.crossref import CrossrefConnector
from pytest_asyncio import fixture
from typing import List, Dict
from unittest.mock import patch, MagicMock

class MockSettings:
    CROSSREF_EMAIL = "test@example.com"
    CROSSREF_RATE_LIMIT = 0.1  # Fast for testing

@fixture
async def crossref_connector():
    """Fixture that provides a CrossrefConnector instance"""
    with patch('app.services.ingestion.sources.crossref.settings', MockSettings()):
        connector = CrossrefConnector()
        yield connector
        if connector.session:
            await connector.session.close()

@pytest.mark.asyncio
async def test_real_crossref_search(crossref_connector):
    """Test a real Crossref search with a query about cow social relationships"""
    query = "cow/animal social relationships cognition"  # Scientific terms for cow friendships
    print(f"\nTesting Crossref search with query: {query}")
    
    results: List[Dict] = await crossref_connector.fetch_papers(query, max_results=5)
    
    print("\nDetailed Results from Crossref:")
    for i, paper in enumerate(results, 1):
        print(f"\nPaper {i}:")
        print(f"Title: {paper['title']}")
        print(f"DOI: {paper['metadata']['doi']}")
        print(f"Year: {paper['metadata']['year']}")
        print(f"Type: {paper['metadata']['type']}")
        print(f"Citations: {paper['metadata']['citations']}")
        print(f"Authors: {', '.join(author['name'] for author in paper['metadata']['authors'])}")
        if paper['metadata'].get('abstract'):
            print(f"\nAbstract ({len(paper['metadata']['abstract'])} chars):")
            print(f"{paper['metadata']['abstract'][:500]}...")
        else:
            print("\nNo abstract available")
        print("-" * 80)
    
    assert len(results) > 0, "No results returned"
    
    # Test first result quality
    first_paper = results[0]
    assert first_paper['title'], "Paper should have a title"
    assert first_paper['metadata']['doi'], "Paper should have a DOI"
    assert first_paper['metadata']['authors'], "Paper should have authors"
    
    # Print stats
    papers_with_abstracts = sum(1 for p in results if p['metadata']['abstract'])
    print(f"\nStats:")
    print(f"Total papers found: {len(results)}")
    print(f"Papers with abstracts: {papers_with_abstracts}")
    print(f"Abstract rate: {papers_with_abstracts/len(results)*100:.1f}%")

@pytest.mark.asyncio
async def test_crossref_error_handling(crossref_connector):
    """Test error handling with invalid queries"""
    # Mock empty query response
    empty_response = {'message': {'items': []}}
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.__aenter__.return_value = mock_response
        mock_response.json.return_value = empty_response
        mock_get.return_value = mock_response
        
        # Test with empty query
        results = await crossref_connector.fetch_papers("", max_results=5)
        assert len(results) == 0, "Empty query should return no results"
        
        # Test with very long query
        results = await crossref_connector.fetch_papers("a" * 1000, max_results=5)
        assert len(results) == 0, "Invalid query should return no results"

@pytest.mark.asyncio
async def test_crossref_max_results(crossref_connector):
    """Test max_results parameter"""
    results = await crossref_connector.fetch_papers("cows social relationships", max_results=3)
    assert len(results) <= 3, "Should respect max_results parameter"

@pytest.mark.asyncio
async def test_crossref_data_quality(crossref_connector):
    """Test quality of returned data"""
    results = await crossref_connector.fetch_papers("Deep Learning", max_results=5)
    
    for paper in results:
        # Basic structure tests
        assert isinstance(paper['id'], str)
        assert isinstance(paper['title'], str)
        assert isinstance(paper['content'], str)
        assert isinstance(paper['url'], str)
        assert isinstance(paper['metadata'], dict)
        
        # Metadata quality tests
        metadata = paper['metadata']
        assert isinstance(metadata['authors'], list)
        if metadata['authors']:
            author = metadata['authors'][0]
            assert 'name' in author
            assert 'affiliations' in author
        
        # DOI format test - allow for complex DOIs
        assert '/' in metadata['doi'], "DOI should contain at least one '/'"
        assert metadata['doi'].startswith('10.'), "DOI should start with '10.'"
        
        # Year format test
        if metadata['year']:
            assert isinstance(metadata['year'], (int, str))
            assert len(str(metadata['year'])) == 4, "Invalid year format"
        
        # Citations count test
        assert isinstance(metadata['citations'], int)
        assert metadata['citations'] >= 0, "Invalid citation count"