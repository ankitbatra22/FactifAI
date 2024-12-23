from pinecone import Pinecone
from app.config import settings
from app.services.embeddings import EmbeddingService

class IngestionService:
    def __init__(self):
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index = self.pc.Index(settings.PINECONE_INDEX)
        self.embedding_service = EmbeddingService()
    
    async def ingest_paper(self, paper: dict) -> bool:
        """
        Ingest a single paper into Pinecone
        """
        # Create embedding from title + abstract
        text_to_embed = f"{paper['title']} {paper['abstract']}"
        vector = self.embedding_service.get_embedding(text_to_embed)
        
        # Metadata to store
        metadata = {
            "title": paper["title"],
            "abstract": paper["abstract"][:1400],  # Limit abstract length
            "url": paper["url"]
        }
        
        try:
            self.index.upsert(
                vectors=[{
                    "id": paper["id"],
                    "values": vector,
                    "metadata": metadata
                }]
            )
            return True
        except Exception as e:
            print(f"Error ingesting paper: {e}")
            return False