from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PINECONE_API_KEY: str
    PINECONE_INDEX: str = "querie"

    class Config:
        env_file = ".env"

settings = Settings()