from pydantic import BaseModel
from typing import List

class SearchQuery(BaseModel):
    query: str

class ResearchPaper(BaseModel):
    title: str
    summary: str
    url: str
    confidence: float

class SearchResponse(BaseModel):
    results: List[ResearchPaper]