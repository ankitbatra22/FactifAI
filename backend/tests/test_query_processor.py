from app.services.query.processor import QueryProcessor
from app.schemas.query import ProcessedQuery, ProcessedQueryLLM
import pytest
import asyncio

@pytest.mark.asyncio
async def test_basic_query_process():
    processor = QueryProcessor()
    query = "Can cows make friends?"
    result = await processor.process_query(query)
    print(result.processed_result.academic_terms)
    assert result.processed_result.is_valid, "Query should be valid"

    for term in result.processed_result.academic_terms:
        assert "cow" in term or "social" in term, "Academic terms should be extracted correctly"


@pytest.mark.asyncio
async def test_invalid_query_process():
    processor = QueryProcessor()
    query = "Hello!"
    result = await processor.process_query(query)
    assert not result.processed_result.is_valid, "Query should be invalid"

@pytest.mark.asyncio
async def test_invalid_query_process_2():
    processor = QueryProcessor()
    query = "What is the capital of France?"
    result = await processor.process_query(query)
    assert not result.processed_result.is_valid, "Query should be invalid"

@pytest.mark.asyncio
async def test_invalid_query_process_3():
    processor = QueryProcessor()
    query = "Cows are fat"
    result = await processor.process_query(query)
    assert not result.processed_result.is_valid, "Query should be invalid"

@pytest.mark.asyncio
async def test_invalid_query_process_4():
    processor = QueryProcessor()
    query = "What is a dog?"
    result = await processor.process_query(query)
    assert not result.processed_result.is_valid, "Query should be invalid"

@pytest.mark.asyncio
async def test_empty_query_process():
    processor = QueryProcessor()
    query = ""
    result = await processor.process_query(query)
    assert not result.processed_result.is_valid, "Query should be invalid"

@pytest.mark.asyncio
async def test_long_query_process():
    processor = QueryProcessor()
    query = "What is the capital of France? What is the capital of France? What is the capital of France? What is the capital of France? What is the capital of France? What is the capital of France? What is the capital of France? What is the capital of France? What is the capital of France? What is the capital of France?"
    result = await processor.process_query(query)
    assert not result.processed_result.is_valid, "Query should be invalid"

