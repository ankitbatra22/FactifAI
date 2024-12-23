import pytest
from app.services.ingestion.pipeline import SearchPipeline
from app.services.embeddings import EmbeddingService
from app.services.search.search import SearchService

@pytest.mark.asyncio
async def test_fetch_from_sources():
    """Test fetching from academic sources"""
    print("\n=== Testing Individual Sources ===")
    
    print("Initializing Pipeline...")
    pipeline = SearchPipeline()
    query = "machine learning neural networks"
    
    print(f"\nTesting query: {query}")
    for source_name, connector in pipeline.sources.items():
        print(f"\nFetching from {source_name}...")
        results = await pipeline._fetch_from_source(
            source_name=source_name,
            connector=connector,
            query=query
        )
        
        print(f"Got {len(results)} results from {source_name}")
        if results:
            print(f"Sample title: {results[0]['title']}")

    print("\n=== Source Testing Complete ===")

@pytest.mark.asyncio
async def test_full_pipeline():
    """Test end-to-end pipeline functionality"""
    print("\n=== Starting Pipeline Test ===")
    
    print("Initializing Pipeline...")
    pipeline = SearchPipeline()
    
    query = "recent advances in quantum computing"
    print(f"\nSearching for: {query}")
    
    print("Fetching results...")
    results = await pipeline.search(query, top_k=5)
    
    print(f"\nGot {len(results)} results")
    
    print("\nPipeline Results:")
    print("-" * 50)
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['title']}")
        print(f"Source: {result['source']}")
        print(f"Score: {result['score']:.3f}")
        print(f"URL: {result['url']}")
    
    print("\n=== Pipeline Test Complete ===")

@pytest.mark.asyncio
async def test_embedding_calculation():
    """Test embedding generation and similarity calculation"""
    pipeline = SearchPipeline()
    
    # Test text to embedding
    text1 = "quantum computing applications"
    text2 = "quantum computer algorithms"
    
    embedding1 = await pipeline._get_embedding_async(text1)
    embedding2 = await pipeline._get_embedding_async(text2)
    
    assert isinstance(embedding1, list)
    assert isinstance(embedding2, list)
    assert len(embedding1) > 0
    
    # Test similarity calculation
    similarity = pipeline._calculate_similarity(embedding1, embedding2)
    assert 0 <= similarity <= 1
    print(f"\nSimilarity score between related texts: {similarity:.3f}")

@pytest.mark.asyncio
async def test_error_handling():
    """Test pipeline error handling"""
    pipeline = SearchPipeline()
    
    # Test with empty query
    results = await pipeline.search("", top_k=3)
    assert isinstance(results, list)
    assert len(results) == 0
    
    # Test with invalid query
    results = await pipeline.search("@#$%^&*", top_k=3)
    assert isinstance(results, list)
    
    # Test with very long query
    long_query = "test " * 100
    results = await pipeline.search(long_query, top_k=3)
    assert isinstance(results, list)

def test_pipeline_initialization():
    """Test pipeline initialization and configuration"""
    pipeline = SearchPipeline()
    
    # Check services initialization
    assert pipeline.embedding_service is not None
    assert isinstance(pipeline.embedding_service, EmbeddingService)
    
    # Check sources initialization
    assert len(pipeline.sources) > 0
    assert all(connector is not None for connector in pipeline.sources.values())
    
    print("\nInitialized Sources:")
    for source_name in pipeline.sources:
        print(f"- {source_name}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 