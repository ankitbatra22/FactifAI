from pydantic import BaseModel
from typing import List, Optional

class Finding(BaseModel):
    """A research finding with its source link"""
    text: str
    source_url: str

class ResearchSummary(BaseModel):
    """Research summary with key findings"""
    summary: str
    findings: List[Finding]
    error: Optional[str] = None