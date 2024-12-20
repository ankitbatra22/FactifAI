from typing import List, Dict
import aiohttp
import re
from app.services.ingestion.sources.base import BaseSourceConnector
from app.config import settings

class OpenAlexConnector(BaseSourceConnector):
    def __init__(self):
        super().__init__()
        self.rate_limit = settings.OPEN_ALEX_RATE_LIMIT
        self.base_url = "https://api.openalex.org/works"
        self.email = settings.OPEN_ALEX_EMAIL
        
    def clean_abstract(self, text: str) -> str:
        """Clean abstract text by removing HTML and unnecessary metadata"""
        if not text:
            return ""
            
        # Remove common patterns that indicate metadata
        patterns_to_remove = [
            r'Journal of.*?\d+',  # Journal references
            r'Volume \d+.*?\d+',  # Volume numbers
            r'First published:.*?(?=\n|$)',  # Publication dates
            r'https?://\S+',  # URLs
            r'DOI:.*?(?=\n|$)',  # DOI references
            r'Citations:.*?(?=\n|$)',  # Citation counts
            r'\(e-mail:.*?\)',  # Email addresses
            r'Search for more papers.*?(?=\n|$)',  # Search suggestions
            r'Please review.*?(?=\n|$)',  # Usage terms
            r'Share.*?(?=\n|$)',  # Share buttons
            r'Copyright.*?(?=\n|$)',  # Copyright notices
            r'\d+\.\s+\w+,\s+\d+',  # Section numbers
            r'The Faculty of.*?publications:',  # Dissertation headers
            r'The dissertation is based.*?publications:',  # Publication lists
            r'Professor.*?Dean',  # Administrative text
            r'Public defence will.*?\d{4}',  # Defense details
            r'[A-Z][a-z]+ [A-Z][a-z]+\s+et al\.,?\s+\d{4}',  # Citation patterns
            r'\([A-Za-z\s]+,\s+\d{4}\)',  # Citation patterns
            r'Chapter \d+.*?(?=\n|$)',  # Chapter headers
            r'Part [IVX]+.*?(?=\n|$)',  # Part headers
            r'Preface.*?(?=\n|$)',  # Front matter
            r'Acknowledgments.*?(?=\n|$)',  # Front matter
            r'Abstract.*?(?=\n|$)',  # Abstract headers
            r'\*Contributed equally.*?(?=\n|$)',  # Author contributions
        ]
        
        text = text.strip()
        for pattern in patterns_to_remove:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
            
        # Remove multiple spaces and newlines
        text = re.sub(r'\s+', ' ', text)
        
        # Remove any remaining citation-like patterns
        text = re.sub(r'\(\d{4}\)', '', text)  # Remove year citations
        text = re.sub(r'\[[\d,\s]+\]', '', text)  # Remove numbered citations
        
        return text.strip()

    async def fetch_papers(self, query: str, max_results: int = 100) -> List[Dict]:
        """Fetch papers from OpenAlex based on query"""
        try:
            session = await self.get_session()
            params = {
                'search': query,
                'per_page': min(max_results, 100),
                'mailto': self.email,
                'select': 'id,title,abstract_inverted_index,authorships,publication_year,cited_by_count,type,open_access,doi,concepts'
            }
            
            print(f"\nQuerying OpenAlex: {self.base_url}")
            print(f"Params: {params}")
            
            async with session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"\nGot response from OpenAlex. Found {len(data.get('results', []))} results")
                    results = []
                    
                    for work in data.get('results', []):
                        try:
                            # Get and clean abstract
                            raw_abstract = self.convert_inverted_index_to_text(
                                work.get('abstract_inverted_index', {})
                            )
                            clean_abstract = self.clean_abstract(raw_abstract)
                            
                            if len(clean_abstract) < 50:  # Skip if abstract is too short after cleaning
                                continue
                                
                            # Extract authors
                            authors = []
                            for authorship in work.get('authorships', []):
                                author = authorship.get('author', {})
                                institutions = [
                                    inst.get('display_name', '')
                                    for inst in authorship.get('institutions', [])
                                ]
                                authors.append({
                                    'name': author.get('display_name', ''),
                                    'affiliations': institutions
                                })
                            
                            # Format content
                            content = (
                                f"Abstract:\n{clean_abstract}\n\n"
                                f"Authors:\n" + '\n'.join(f"- {author['name']}" for author in authors) + "\n\n"
                                f"Year: {work.get('publication_year', '')}\n"
                                f"Citations: {work.get('cited_by_count', 0)}"
                            )
                            
                            paper = {
                                'id': f"openalex_{work['id']}",
                                'title': work.get('title', ''),
                                'content': content,
                                'url': f"https://doi.org/{work['doi']}" if work.get('doi') else '',
                                'source': 'openalex',
                                'metadata': {
                                    'authors': authors,
                                    'year': work.get('publication_year'),
                                    'citations': work.get('cited_by_count', 0),
                                    'type': work.get('type'),
                                    'abstract': clean_abstract,
                                    'concepts': work.get('concepts', []),
                                    'doi': work.get('doi')
                                }
                            }
                            results.append(paper)
                            
                        except Exception as e:
                            print(f"Error processing work: {e}")
                            continue
                    
                    print(f"Successfully processed {len(results)} papers")
                    return results
                    
                else:
                    print(f"Error from OpenAlex API: {response.status}")
                    return []
                    
        except Exception as e:
            print(f"Error fetching from OpenAlex: {str(e)}")
            return []

    def _extract_authors(self, work: Dict) -> List[Dict]:
        """Extract author information from work data"""
        authors = []
        for authorship in work.get('authorships', []):
            author = authorship.get('author', {})
            authors.append({
                'name': author.get('display_name', ''),
                'id': author.get('id', '')
            })
        return authors

    def convert_inverted_index_to_text(self, inverted_index: Dict) -> str:
        """Convert OpenAlex's inverted index format to regular text"""
        if not inverted_index:
            return ""
            
        try:
            word_positions = []
            for word, positions in inverted_index.items():
                for pos in positions:
                    word_positions.append((pos, word))
            
            return ' '.join(word for _, word in sorted(word_positions))
        except Exception as e:
            print(f"Error converting inverted index: {e}")
            return "" 