from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class PaperMetadata(BaseModel):
    """
    Flexible metadata for academic papers.
    All fields optional to accommodate different source APIs.
    """
    authors: List[str] = []
    year: Optional[int] = None
    published_date: Optional[datetime] = None
    citations: Optional[int] = None
    categories: List[str] = []
    abstract: Optional[str] = None
    doi: Optional[str] = None
    type: Optional[str] = None

class Paper(BaseModel):
    """
    Core paper data structure.
    """
    title: str
    url: str
    metadata: PaperMetadata 