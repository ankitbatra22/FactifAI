from typing import List, Dict, AsyncGenerator
import asyncio
from datetime import datetime
from pinecone import Pinecone
from app.services.embeddings import EmbeddingService
from app.services.search.search import SearchService
from app.services.ingestion.sources.base import BaseSourceConnector
from app.config import settings
from app.services.ingestion.sources.arxiv import ArxivConnector
from app.services.ingestion.sources.open_alex import OpenAlexConnector
from app.schemas.paper import Paper

class SearchPipeline:
    sources = {
        'arxiv': ArxivConnector(),          # ~100 results
        #'pubmed': PubMedConnector(),        # ~100 results  # temporarily disabled (poor results)
        #'crossref': CrossrefConnector(),    # ~100 results  # temporarily disabled (inconsistent results/lacking information)
        'open_alex': OpenAlexConnector(),  # ~100 results
        
        # TODO: Future Sources
        # ... existing comments ...
    }
    
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.pinecone_client = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index = self.pinecone_client.Index(settings.PINECONE_INDEX)
        
    async def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Real-time search across all sources
        Expected total: ~200-300 results to process
        """
        start_time = datetime.now()
        
        # Fetch ~100 results from each source concurrently
        all_results = await self._fetch_from_all_sources(query)
        print(f"Fetched {len(all_results)} total results in {datetime.now() - start_time}")
        
        # Generate query embedding once
        query_embedding = self.embedding_service.get_embedding(query)
        
        # Process in batches of 50 for memory efficiency
        batch_size = 50
        ranked_results = []
        
        for i in range(0, len(all_results), batch_size):
            batch = all_results[i:i + batch_size]
            batch_ranked = await self._rank_results(query_embedding, batch)
            ranked_results.extend(batch_ranked)
            
            # Sort and keep top results so far
            ranked_results.sort(key=lambda x: x['score'], reverse=True)
            ranked_results = ranked_results[:top_k]
        
        print(f"Total search time: {datetime.now() - start_time}")
        return ranked_results

    async def _fetch_from_source(
        self, 
        source_name: str, 
        connector: BaseSourceConnector, 
        query: str,
        max_results: int = 50
    ) -> List[Dict]:
        """
        Fetch up to max_results from a single source
        """
        try:
            papers: List[Paper] = await connector.fetch_papers(query, max_results=max_results)
            print(f"Fetched {len(papers)} papers from {source_name}")
            
            # Convert Paper objects to dict with only needed fields
            return [{
                'title': paper.title,
                'abstract': paper.metadata.abstract,
                'url': paper.url,
                'source': source_name,
                'categories': paper.metadata.categories,
                'authors': paper.metadata.authors,
                'year': paper.metadata.year
            } for paper in papers]
            
        except Exception as e:
            print(f"Error fetching from {source_name}: {str(e)}")
            return []

    async def _fetch_from_all_sources(self, query: str) -> List[Dict]:
        """
        Fetch results from all sources concurrently
        """
        tasks = []
        for source_name, connector in self.sources.items():
            # Adjust max_results based on source
            max_results = 50
            task = self._fetch_from_source(
                source_name=source_name, 
                connector=connector, 
                query=query, 
                max_results=max_results
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine results, excluding any errors
        all_documents: List[Dict] = []
        for result in results:
            if isinstance(result, list):
                all_documents.extend(result)
        
        return all_documents

    async def _rank_results(
        self,
        query_embedding: List[float],
        documents: List[Dict]
    ) -> List[Dict]:
        """
        Rank a batch of results based on relevance to query
        """
        scored_docs = []
        
        # Process embeddings in parallel for the batch
        embedding_tasks = []
        for doc in documents:
            doc_text = f"{doc['title']} {doc['abstract'][:1000]}"
            task = asyncio.create_task(
                self._get_embedding_async(doc_text)
            )
            embedding_tasks.append((doc, task))
        
        # Wait for all embeddings
        for doc, task in embedding_tasks:
            try:
                doc_embedding = await task
                similarity = self._calculate_similarity(
                    query_embedding, 
                    doc_embedding
                )
                
                doc['score'] = similarity
                scored_docs.append(doc)
            except Exception as e:
                print(f"Error processing document: {str(e)}")
                continue
        
        return scored_docs

    async def _get_embedding_async(self, text: str) -> List[float]:
        """
        Wrapper to make embedding generation async
        """
        return self.embedding_service.get_embedding(text)

    def _calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings
        """
        return sum(a * b for a, b in zip(embedding1, embedding2)) / (sum(a**2 for a in embedding1) * sum(b**2 for b in embedding2))

    def _chunk_content(self, content: str, chunk_size: int = 1000):
        """
        Split content into semantic chunks
        """
        # Simple chunking for now - could be improved with semantic splitting
        return [content[i:i + chunk_size] for i in range(0, len(content), chunk_size)]

    async def upsert_to_pinecone(self, processed_docs: List[Dict]):
        if processed_docs:
            self.index.upsert(vectors=processed_docs) 