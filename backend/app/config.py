from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PINECONE_API_KEY: str
    PINECONE_INDEX: str = "querie"
    ARXIV_RATE_LIMIT: float = Field(default=3.0)  # 3 seconds between requests
    MAX_WORKERS: int = Field(default=4)

    class Config:
        env_file = ".env"

settings = Settings()