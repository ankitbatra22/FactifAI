from typing import List
from pinecone import Pinecone
from app.config import settings
from app.schemas.search import ResearchPaper
from app.services.embeddings import EmbeddingService

class SearchService:
    def __init__(self):
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index = self.pc.Index(settings.PINECONE_INDEX)
        self.embedding_service = EmbeddingService()
    
    async def search(self, query: str) -> List[ResearchPaper]:
        # Convert query to vector
        query_vector = self.embedding_service.get_embedding(query)
        
        # Search in Pinecone
        results = self.index.query(
            vector=query_vector,
            top_k=3,
            include_metadata=True
        )
        
        # Convert to ResearchPaper objects
        papers = []
        for match in results.matches:
            papers.append(
                ResearchPaper(
                    title=match.metadata["title"],
                    summary=match.metadata["abstract"],
                    url=match.metadata["url"],
                    confidence=match.score
                )
            )
        
        return papers