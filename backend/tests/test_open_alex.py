import pytest
from app.services.ingestion.sources.open_alex import OpenAlexConnector
from pytest_asyncio import fixture
from typing import List, Dict
from unittest.mock import patch
from app.schemas.paper import Paper, PaperMetadata

class MockSettings:
    OPEN_ALEX_EMAIL = "test@example.com"
    OPEN_ALEX_RATE_LIMIT = 0.1  # Fast for testing

@fixture
async def open_alex_connector():
    """Fixture that provides an OpenAlexConnector instance"""
    with patch('app.services.ingestion.sources.open_alex.settings', MockSettings()):
        connector = OpenAlexConnector()
        yield connector
        if connector.session:
            await connector.session.close()

@pytest.mark.asyncio
async def test_real_open_alex_search(open_alex_connector: OpenAlexConnector):
    """Test a real OpenAlex search"""
    query = "Can Cows Make Friends?"
    print(f"\nTesting OpenAlex search with query: {query}")
    
    papers: List[Paper] = await open_alex_connector.fetch_papers(query, max_results=5)

    print(f"Found {len(papers)} papers")

    for i, paper in enumerate(papers, 1):
        print(f"\nPaper {i}:")
        print(f"Title: {paper.title}")
        if paper.metadata is not None:
            print(f"Abstract: {paper.metadata.abstract}")
            print(f"Authors: {paper.metadata.authors}")
            print(f"Citations: {paper.metadata.citations}")
            print(f"Year: {paper.metadata.year}")
            print(f"URL: {paper.url}")
        else:
            print("No metadata available for this paper")

    
    # Temporarily commented out for migration to new schema
    # print("\nResults from OpenAlex:")
    # for i, paper in enumerate(results, 1):
    #     print(f"\nPaper {i}:")
    #     print(f"Title: {paper['title']}")
    #     if paper['metadata'].get('abstract'):
    #         abstract = paper['metadata']['abstract']
    #         print(f"Abstract ({len(abstract)} chars): {abstract[:900]}...")
    #         # Check for common noise in abstracts
    #         assert 'http' not in abstract.lower(), "Abstract contains URLs"
    #         assert 'doi' not in abstract.lower(), "Abstract contains DOI"
    #         assert 'citation' not in abstract.lower(), "Abstract contains citation info"
    #     else:
    #         print("No abstract")
    #     print(f"Authors: {', '.join(author['name'] for author in paper['metadata']['authors'])}")
    #     print(f"Citations: {paper['metadata']['citations']}")
    #     print(f"Year: {paper['metadata']['year']}")
    #     print(f"URL: {paper['url']}")
    
    # assert len(results) > 0, "No results returned from OpenAlex"
    # assert len(results) <= 5, f"Too many results returned: {len(results)}"
    
    # # Test structure and quality of first result
    # if results:
    #     paper = results[0]
    #     assert 'title' in paper, "Paper missing title"
    #     assert 'content' in paper, "Paper missing content"
    #     assert 'metadata' in paper, "Paper missing metadata"
    #     assert 'abstract' in paper['metadata'], "Paper metadata missing abstract"
        
    #     # Quality checks
    #     if paper['metadata']['abstract']:
    #         abstract = paper['metadata']['abstract']
    #         assert len(abstract) > 50, "Abstract too short"
    #         assert not any(marker in abstract.lower() for marker in ['http', 'doi', 'citation']), \
    #             "Abstract contains metadata markers"