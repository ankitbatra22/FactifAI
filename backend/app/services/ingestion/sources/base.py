from abc import ABC, abstractmethod
from typing import List, Dict
import asyncio
import aiohttp
from app.config import settings

class BaseSourceConnector(ABC):
    def __init__(self):
        self.session = None
        self.rate_limit = 1.0  # Default 1 second between requests
    
    async def get_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session
    
    @abstractmethod
    async def fetch_papers(self, query: str, max_results: int = 100) -> List[Dict]:
        """
        Fetch papers from the source
        Returns list of documents in format:
        {
            'id': str,
            'title': str,
            'content': str,
            'url': str,
            'source': str
        }
        """
        pass
    
    async def rate_limit_wait(self):
        await asyncio.sleep(self.rate_limit) 