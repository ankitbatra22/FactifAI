from pydantic import BaseModel
from typing import List, Optional

class Finding(BaseModel):
    """A research finding with its source link"""
    title: str
    text: str
    source_url: str
    source_name: Optional[str] = None
    source_date: Optional[str] = None

class ResearchSummary(BaseModel):
    """Research summary with key findings"""
    summary: str
    findings: List[Finding]
    error: Optional[str] = None