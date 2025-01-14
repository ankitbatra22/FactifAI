from pydantic import BaseModel, Field
from typing import List, Optional

class ProcessedQueryLLM(BaseModel):
    """OpenAI Function Schema for Query Processing"""
    is_valid: bool = Field(..., description="Whether the query is valid for research")
    academic_term: Optional[str] = Field(
        None,
        description="The academic term derived from the query. Only provide if is_valid=true.",
    )

class ProcessedQuery(BaseModel):
    """Full query processing result"""
    original_query: str
    processed_result: ProcessedQueryLLM
    processing_time: float 