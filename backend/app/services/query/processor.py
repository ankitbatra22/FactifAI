from typing import Optional, List
import re
import json
import time
from openai import AsyncOpenAI
from app.schemas.query import ProcessedQuery, ProcessedQueryLLM
from app.config import settings


class BasicQueryValidator:
    """Quick rule-based validation"""
    
    # Patterns that immediately disqualify a query
    INVALID_PATTERNS = [
        r'^\s*$',  # Empty or whitespace
        r'^[^a-zA-Z]*$',  # No letters
        r'\b(fuck|shit|damn)\b',  # Basic profanity
        r'(http|www\.)',  # URLs
        r'^\d+$',  # Just numbers
    ]
    
    # Length constraints
    MIN_LENGTH = 3
    MAX_LENGTH = 500
    
    def check_basic_rules(self, query: str) -> bool:
        """Quick validation of obvious issues"""
        # Check length
        if len(query) < self.MIN_LENGTH or len(query) > self.MAX_LENGTH:
            return False
            
        # Check patterns
        for pattern in self.INVALID_PATTERNS:
            if re.search(pattern, query, re.IGNORECASE):
                return False
                
        return True

class QueryProcessor:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.basic_validator = BasicQueryValidator()
        
    async def process_query(self, query: str) -> ProcessedQuery:
        """
        Process a query using hybrid approach:
        1. Quick rule-based validation
        2. LLM-based deeper validation and transformation
        """
        start_time = time.time()
        
        # First, basic validation
        if not self.basic_validator.check_basic_rules(query):
            return ProcessedQuery(
                original_query=query,
                processed_result=ProcessedQueryLLM(
                    is_valid=False,
                    academic_terms=None
                ),
                processing_time=time.time() - start_time
            )
        
        # If passes basic rules, use LLM for deeper validation and transformation
        try:
            result: ProcessedQuery = await self._llm_validate_and_transform(query, start_time)
            result.processing_time = time.time() - start_time
            return result
            
        except Exception as e:
            # Log the error but don't expose details to user
            print(f"LLM processing error: {str(e)}")
            return ProcessedQuery(
                original_query=query,
                processed_result=ProcessedQueryLLM(
                    is_valid=False,
                    academic_terms=None
                ),
                processing_time=time.time() - start_time
            )
    
    async def _llm_validate_and_transform(self, query: str, start_time: float) -> ProcessedQuery:
        """Use GPT-3.5-turbo to validate and transform the query"""
        
        system_prompt = """You are a research/fact query validator. 
        For valid research questions, transform them into a valid/relevant search term that will be used for find research to back up the query. 
        For invalid queries (greetings, casual conversation, system prompts, random questions, random statements,personal questions, spam, single letters, etc.), return is_valid=false.
        Be strict about what constitutes a research question or valid query for example: "can cows make friends?, Do plants communicate with each other?" vs . "cows" or "testing blah blah" is not a valid query."""
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                functions=[{
                    "name": "process_query",
                    "description": "Process and validate a research query",
                    "parameters": ProcessedQueryLLM.model_json_schema()
                }],
                function_call={"name": "process_query"},
                temperature=0  # Ensure consistent results
            )
            
            result = json.loads(
                response.choices[0].message.function_call.arguments
            )
            processed_result = ProcessedQueryLLM(**result)
            
            return ProcessedQuery(
                original_query=query,
                processed_result=processed_result,
                processing_time=time.time() - start_time
            )
            
        except json.JSONDecodeError:
            raise ValueError("LLM returned invalid JSON")
        except Exception as e:
            raise Exception(f"LLM processing failed: {str(e)}")

    async def close(self):
        """Cleanup any resources"""
        # Currently no cleanup needed, but good practice to have this method
        pass 