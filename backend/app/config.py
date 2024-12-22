from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PINECONE_API_KEY: str
    PINECONE_INDEX: str

    # Arxiv Settings
    ARXIV_RATE_LIMIT: float = Field(default=3.0)
    
    # PubMed Settings
    PUBMED_EMAIL: str = Field(default="")  # Made optional with default empty string
    #PUBMED_API_KEY: str = Field(default="")  # Optional
    PUBMED_RATE_LIMIT: float = Field(default=0.34)  # NCBI allows 3 requests/second
    
    MAX_WORKERS: int = Field(default=4)

    # Semantic Scholar Settings
    SEMANTIC_SCHOLAR_API_KEY: str = Field(default="")
    SEMANTIC_SCHOLAR_RATE_LIMIT: float = Field(default=100.0)  # 100 requests per 5 minutes

    # Crossref Settings
    CROSSREF_EMAIL: str = "your-email@example.com"
    CROSSREF_RATE_LIMIT: float = 1.0  # requests per second

    class Config:
        env_file = ".env"

settings = Settings()