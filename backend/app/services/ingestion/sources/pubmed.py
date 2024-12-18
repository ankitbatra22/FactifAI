from typing import List, Dict
import asyncio
from datetime import datetime
from easy_entrez import EntrezAPI
from easy_entrez.parsing import xml_to_string
from app.services.ingestion.sources.base import BaseSourceConnector
from app.config import settings

class PubMedConnector(BaseSourceConnector):
    def __init__(self):
        super().__init__()
        self.rate_limit = settings.PUBMED_RATE_LIMIT
        self.api = EntrezAPI(
            'querie',  # your tool name
            settings.PUBMED_EMAIL,
        )
        
    async def fetch_papers(self, query: str, max_results: int = 100) -> List[Dict]:
        """Fetch papers from PubMed based on query"""
        if not query:
            return []
        
        try:
            # Search for papers
            print("\nSearching PubMed for:", query)
            search_result = self.api.search(query, max_results=max_results, database='pubmed')
            
            print("\nSearch response:", search_result.data)
            
            if not search_result.data or 'error' in search_result.data:
                print(f"Error in search response: {search_result.data}")
                return []
            
            if 'esearchresult' not in search_result.data:
                print("Unexpected response format:", search_result.data)
                return []
            
            id_list = search_result.data['esearchresult'].get('idlist', [])
            
            if not id_list:
                print("No IDs found in search results")
                return []
            
            # Fetch full records
            print("\nFetching details for IDs:", id_list)
            fetch_result = self.api.fetch(
                collection=id_list,
                database='pubmed',
                max_results=max_results
            )

            # The response is already an XML Element
            root = fetch_result.data
            
            # Process each article
            results = []
            for article in root.findall('.//PubmedArticle'):
                try:
                    medline_citation = article.find('MedlineCitation')
                    if medline_citation is None:
                        continue
                    
                    article_elem = medline_citation.find('Article')
                    if article_elem is None:
                        continue
                    
                    # Basic metadata
                    pmid = medline_citation.findtext('PMID', '')
                    title = article_elem.findtext('ArticleTitle', '')
                    
                    # Enhanced abstract extraction
                    abstract = ""
                    abstract_elem = article_elem.find('.//Abstract')
                    if abstract_elem is not None:
                        # Handle structured abstracts (with labels like BACKGROUND, METHODS, etc.)
                        abstract_texts = []
                        for abstract_text in abstract_elem.findall('AbstractText'):
                            label = abstract_text.get('Label', '')
                            text = abstract_text.text or ''
                            if label:
                                abstract_texts.append(f"{label}: {text}")
                            else:
                                abstract_texts.append(text)
                        abstract = '\n'.join(abstract_texts)
                    
                    # Enhanced author extraction
                    authors = []
                    for author in article_elem.findall('.//Author'):
                        last_name = author.findtext('LastName', '')
                        fore_name = author.findtext('ForeName', '')
                        affiliations = [aff.text for aff in author.findall('.//Affiliation') if aff.text]
                        if last_name or fore_name:
                            authors.append({
                                'name': f"{fore_name} {last_name}".strip(),
                                'affiliations': affiliations
                            })
                    
                    # Enhanced metadata extraction
                    journal_elem = article_elem.find('.//Journal')
                    journal = {
                        'title': journal_elem.findtext('.//Title', ''),
                        'iso_abbreviation': journal_elem.findtext('.//ISOAbbreviation', ''),
                        'issn': journal_elem.findtext('.//ISSN', '')
                    }
                    
                    # Publication date (more detailed)
                    pub_date_elem = article_elem.find('.//PubDate')
                    pub_date = {}
                    if pub_date_elem is not None:
                        pub_date = {
                            'year': pub_date_elem.findtext('Year', ''),
                            'month': pub_date_elem.findtext('Month', ''),
                            'day': pub_date_elem.findtext('Day', '')
                        }
                    
                    # Keywords and MeSH terms
                    keywords = [keyword.text for keyword in medline_citation.findall('.//KeywordList/Keyword') if keyword.text]
                    mesh_terms = [
                        mesh.findtext('DescriptorName', '')
                        for mesh in medline_citation.findall('.//MeshHeadingList/MeshHeading')
                    ]
                    
                    # DOI and other IDs
                    article_ids = {}
                    for id_elem in article.findall('.//ArticleIdList/ArticleId'):
                        id_type = id_elem.get('IdType', '')
                        if id_type:
                            article_ids[id_type] = id_elem.text
                    
                    paper = {
                        'id': f"pubmed_{pmid}",
                        'title': title,
                        'content': (
                            f"Abstract:\n{abstract}\n\n"
                            f"Authors:\n" + '\n'.join(f"- {author['name']} ({'; '.join(author['affiliations'])})" 
                                                     for author in authors) + "\n\n"
                            f"Journal: {journal['title']}\n"
                            f"Publication Date: {pub_date.get('year', '')}-{pub_date.get('month', '')}-{pub_date.get('day', '')}"
                        ),
                        'url': f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                        'source': 'pubmed',
                        'metadata': {
                            'authors': authors,
                            'journal': journal,
                            'publication_date': pub_date,
                            'pmid': pmid,
                            'doi': article_ids.get('doi', ''),
                            'keywords': keywords,
                            'mesh_terms': mesh_terms,
                            'article_ids': article_ids,
                            'abstract': abstract
                        }
                    }
                    results.append(paper)
                    
                except Exception as e:
                    print(f"Error processing article: {e}")
                    continue
                    
            print(f"\nPubMed returned {len(results)} results for query: {query}")
            return results
            
        except Exception as e:
            print(f"Error fetching from PubMed: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return []