from typing import List, Dict
import aiohttp
import re
from app.services.ingestion.sources.base import BaseSourceConnector
from app.config import settings
import json

class CrossrefConnector(BaseSourceConnector):
    def __init__(self):
        super().__init__()
        self.base_url = "https://api.crossref.org/works"
        self.email = settings.CROSSREF_EMAIL
        
    def clean_abstract(self, abstract: str) -> str:
        """Clean abstract text by removing XML tags and normalizing whitespace"""
        if not abstract:
            return ""
            
        # Simple regex to remove XML/JATS tags
        text = re.sub(r'<[^>]+>', '', abstract)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
            
    async def fetch_papers(self, query: str, max_results: int = 100) -> List[Dict]:
        """Fetch papers from Crossref based on query"""
        if not query.strip():
            return []
            
        try:
            session = await self.get_session()
            params = {
                'query': query,
                'rows': min(max_results * 2, 100),  # Fetch more since we'll filter some out
                'mailto': self.email,
                'select': 'DOI,title,abstract,author,published-print,type,reference,is-referenced-by-count'
            }
            
            print(f"\nQuerying Crossref API:")
            print(f"URL: {self.base_url}")
            print(f"Params: {json.dumps(params, indent=2)}")
            
            async with session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    #print(f"Data: {json.dumps(data, indent=2)}")
                    results = []
                    
                    for work in data['message'].get('items', []):
                        try:
                            # Skip if no abstract
                            raw_abstract = work.get('abstract', '')
                            if not raw_abstract:
                                continue
                                
                            title = work.get('title', [''])[0]
                            doi = work.get('DOI', '')
                            cleaned_abstract = self.clean_abstract(raw_abstract)
                            
                            # Double check we still have an abstract after cleaning
                            if not cleaned_abstract:
                                continue
                                
                            processed_paper = {
                                'id': f"crossref_{doi}",
                                'title': title,
                                'content': cleaned_abstract,
                                'url': f"https://doi.org/{doi}",
                                'source': 'crossref',
                                'metadata': {
                                    'authors': [
                                        {
                                            'name': f"{author.get('given', '')} {author.get('family', '')}".strip(),
                                            'affiliations': author.get('affiliation', [])
                                        }
                                        for author in work.get('author', [])
                                    ],
                                    'year': work.get('published-print', {}).get('date-parts', [['']])[0][0],
                                    'type': work.get('type'),
                                    'citations': work.get('is-referenced-by-count', 0),
                                    'abstract': cleaned_abstract,
                                    'doi': doi,
                                    'references': work.get('reference', [])
                                }
                            }
                            results.append(processed_paper)
                            
                        except Exception as e:
                            print(f"Error processing work: {e}")
                            continue
                    
                    return results[:max_results]
                    
                else:
                    print(f"Error response from Crossref: {response.status}")
                    print(await response.text())
                    
            return []
            
        except Exception as e:
            print(f"Error fetching from Crossref: {str(e)}")
            return [] 