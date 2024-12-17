from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.schemas.search import SearchQuery, SearchResponse
from app.services.search import SearchService

app = FastAPI(title="Querie")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

search_service = SearchService()

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/search", response_model=SearchResponse)
async def search_papers(query: SearchQuery):
    results = await search_service.search(query.query)
    return SearchResponse(results=results)