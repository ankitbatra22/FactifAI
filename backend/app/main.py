from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.schemas.search import SearchQuery, SearchResponse, ResearchPaper
from app.orchestration.search import SearchOrchestrator
from app.config import settings

app = FastAPI(title="Querie")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

search_orchestrator = SearchOrchestrator()

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/search", response_model=SearchResponse)
async def search_papers(query: SearchQuery):
    """
    Search endpoint that combines academic papers and web results
    """
    try:
        search_response= await search_orchestrator.search(query.query)
        return search_response
    
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Search error: {str(e)}")  # Log the error
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your search"
        )

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup when shutting down"""
    await search_orchestrator.query_processor.close()