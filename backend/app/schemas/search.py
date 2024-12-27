from pydantic import BaseModel
from typing import List, Optional
from app.schemas.research_summary import ResearchSummary
class SearchQuery(BaseModel):
    query: str

class ResearchPaper(BaseModel):
    title: str
    summary: str
    url: str
    confidence: float

class SearchResponse(BaseModel):
    is_valid: bool
    papers: List[ResearchPaper]
    web_summary: Optional[ResearchSummary]
    