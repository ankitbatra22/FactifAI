from typing import List, Dict
import aiohttp
from app.services.ingestion.sources.base import BaseSourceConnector
from app.config import settings

class SemanticScholarConnector(BaseSourceConnector):
    def __init__(self):
        super().__init__()
        self.rate_limit = settings.SEMANTIC_SCHOLAR_RATE_LIMIT  # Usually 100 requests per 5 minutes
        self.api_key = settings.SEMANTIC_SCHOLAR_API_KEY
        self.base_url = "https://api.semanticscholar.org/graph/v1"
        
    async def fetch_papers(self, query: str, max_results: int = 100) -> List[Dict]:
        """Fetch papers from Semantic Scholar based on query"""
        if not query:
            return []
            
        try:
            session = await self.get_session()
            
            # Search endpoint
            search_url = f"{self.base_url}/paper/search"
            params = {
                'query': query,
                'limit': min(max_results, 100),  # API limit is 100 per request
                'fields': 'title,abstract,authors,year,venue,publicationVenue,citations,references,externalIds,url,fieldsOfStudy,tldr'
            }
            headers = {"x-api-key": self.api_key}
            
            async with session.get(search_url, params=params, headers=headers) as response:
                if response.status != 200:
                    print(f"Error from Semantic Scholar API: {response.status}")
                    return []
                    
                data = await response.json()
                papers = data.get('data', [])
                
                results = []
                for paper in papers:
                    # Extract authors with affiliations
                    authors = []
                    for author in paper.get('authors', []):
                        authors.append({
                            'name': author.get('name', ''),
                            'affiliations': author.get('affiliations', [])
                        })
                    
                    # Get TLDR (AI-generated summary) if available
                    tldr = paper.get('tldr', {}).get('text', '')
                    
                    # Format content
                    content = (
                        f"Abstract:\n{paper.get('abstract', '')}\n\n"
                        f"TLDR:\n{tldr}\n\n" if tldr else ""
                        f"Authors:\n" + '\n'.join(f"- {author['name']}" for author in authors) + "\n\n"
                        f"Venue: {paper.get('venue', '')}\n"
                        f"Year: {paper.get('year', '')}\n"
                        f"Citations: {len(paper.get('citations', []))}\n"
                        f"Fields of Study: {', '.join(paper.get('fieldsOfStudy', []))}"
                    )
                    
                    # Extract external IDs
                    external_ids = paper.get('externalIds', {})
                    
                    result = {
                        'id': f"semantic_{paper.get('paperId', '')}",
                        'title': paper.get('title', ''),
                        'content': content,
                        'url': paper.get('url', ''),
                        'source': 'semantic_scholar',
                        'metadata': {
                            'authors': authors,
                            'year': paper.get('year'),
                            'venue': paper.get('venue'),
                            'publication_venue': paper.get('publicationVenue'),
                            'citation_count': len(paper.get('citations', [])),
                            'reference_count': len(paper.get('references', [])),
                            'fields_of_study': paper.get('fieldsOfStudy', []),
                            'abstract': paper.get('abstract', ''),
                            'tldr': tldr,
                            'external_ids': {
                                'doi': external_ids.get('DOI'),
                                'arxiv': external_ids.get('ArXiv'),
                                'pubmed': external_ids.get('PubMed'),
                                'mag': external_ids.get('MAG')
                            }
                        }
                    }
                    results.append(result)
                    
                    # Respect rate limit
                    await self.rate_limit_wait()
                    
                print(f"Semantic Scholar returned {len(results)} results for query: {query}")
                return results
                
        except Exception as e:
            print(f"Error fetching from Semantic Scholar: {str(e)}")
            return [] 