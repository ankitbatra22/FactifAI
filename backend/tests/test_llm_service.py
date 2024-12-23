import pytest
from app.services.llm.llm_service import LLMService
from app.services.search.google_search import GoogleSearchService

@pytest.mark.asyncio
async def test_llm_summary():
    """Test end-to-end LLM summary generation"""
    search_service = GoogleSearchService(num_results=5)
    search_results = await search_service.search(
        #"Do cows form friendships"
        "Is homeschooling more effective than traditional schooling?"
    )

    assert search_results, "Should have search results to analyze"

    # Generate summary
    llm_service = LLMService()
    summary = await llm_service.generate_summary(
        #"Do cows form friendships?",
        "Is homeschooling more effective than traditional schooling?",
        search_results
    )

    # Validate structure
    assert summary.summary, "Should have a summary"
    assert len(summary.findings) > 0, "Should have findings"
    assert not summary.error, "Should not have errors"

    # Print results
    print("\nResearch Summary:")
    print("-" * 50)
    print(f"\n{summary.summary}")

    print("\nRelevant Findings:")
    for finding in summary.findings:
        print(f"\n- {finding.text}")
        print(f"  Source: {finding.source_url}")

@pytest.mark.asyncio
async def test_error_handling():
    """Test handling of empty results"""
    llm_service = LLMService()
    summary = await llm_service.generate_summary(
        "Test query",
        []  # Empty results
    )
    

    assert not summary.findings, "Should have no findings"
    assert summary.summary == "No search results available."
    assert summary.error == "No search results to analyze"