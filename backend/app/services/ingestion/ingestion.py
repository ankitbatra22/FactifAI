from pinecone import Pinecone
from app.config import settings
from app.services.embeddings import EmbeddingService
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from typing import List, Dict
from tqdm import tqdm

logger = logging.getLogger(__name__)

class IngestionService:
    def __init__(self):
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index = self.pc.Index(settings.PINECONE_INDEX)
        self.embedding_service = EmbeddingService()
        self.batch_size = 50  # Configurable batch size
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def ingest_paper(self, paper: dict) -> bool:
        """
        Ingest a single paper into Pinecone with retry logic
        """
        try:
            # Create embedding from title + abstract
            text_to_embed = f"{paper['title']} {paper['abstract']}"
            vector = self.embedding_service.get_embedding(text_to_embed)
            
            # Metadata to store
            metadata = {
                "title": paper["title"],
                "abstract": paper["abstract"][:1400],  # Limit abstract length
                "url": paper["url"]
            }
            
            self.index.upsert(
                vectors=[{
                    "id": paper["id"],
                    "values": vector,
                    "metadata": metadata
                }]
            )
            return True
        except Exception as e:
            logger.error(f"Error ingesting paper {paper['id']}: {str(e)}")
            raise

    async def batch_ingest_papers(self, papers: List[Dict]) -> None:
        """
        Batch ingest papers with progress tracking and error handling
        """
        if not papers:
            return

        total_batches = (len(papers) + self.batch_size - 1) // self.batch_size
        failed_papers = []

        with tqdm(total=total_batches, desc="Batches") as pbar:
            for i in range(0, len(papers), self.batch_size):
                batch = papers[i:i + self.batch_size]
                vectors = []
                
                # Prepare batch
                for paper in batch:
                    try:
                        text_to_embed = f"{paper['title']} {paper['abstract']}"
                        vector = self.embedding_service.get_embedding(text_to_embed)
                        
                        vectors.append({
                            "id": paper["id"],
                            "values": vector,
                            "metadata": {
                                "title": paper["title"],
                                "abstract": paper["abstract"][:1400],
                                "url": paper["url"]
                            }
                        })
                    except Exception as e:
                        logger.error(f"Error preparing paper {paper['id']}: {str(e)}")
                        failed_papers.append(paper["id"])
                        continue

                # Attempt batch upsert with retry
                try:
                    if vectors:
                        await self._batch_upsert_with_retry(vectors)
                except Exception as e:
                    logger.error(f"Batch upsert failed for batch {i//self.batch_size + 1}: {str(e)}")
                    failed_papers.extend([v["id"] for v in vectors])
                finally:
                    pbar.update(1)

        if failed_papers:
            logger.warning(f"Failed to ingest {len(failed_papers)} papers: {failed_papers}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def _batch_upsert_with_retry(self, vectors: List[Dict]) -> None:
        """
        Attempt batch upsert with retry logic
        """
        try:
            self.index.upsert(vectors=vectors)
        except Exception as e:
            logger.error(f"Batch upsert error: {str(e)}")
            raise