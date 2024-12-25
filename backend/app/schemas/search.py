from pydantic import BaseModel
from typing import List
from app.schemas.research_summary import ResearchSummary
class SearchQuery(BaseModel):
    query: str

class ResearchPaper(BaseModel):
    title: str
    summary: str
    url: str
    confidence: float

class SearchResponse(BaseModel):
    papers: List[ResearchPaper]
    web_summary: ResearchSummary
    