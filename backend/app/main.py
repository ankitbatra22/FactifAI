from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
from app.schemas.search import SearchQuery, SearchResponse, ResearchPaper
from app.orchestration.search import SearchOrchestrator
from app.config import settings

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="FactifAI")

# Custom rate limit handler
@app.exception_handler(RateLimitExceeded)
async def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Currently free users are limited to 10 queries per hour. Premium version coming soon!"
        }
    )

app.state.limiter = limiter

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

search_orchestrator = SearchOrchestrator()

@app.get("/")
async def root():
    return {"message": "Welcome to the FactifAI API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/search", response_model=SearchResponse)
@limiter.limit("20/hour")  # Allow 10 requests per hour per IP
async def search_papers(request: Request, query: SearchQuery):
    """
    Search endpoint that combines academic papers and web results
    """
    try:
        search_response = await search_orchestrator.search(query.query)
        return search_response
    
    except HTTPException as exception:
        raise exception
    except Exception as e:
        print(f"Search error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your search"
        )

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup when shutting down"""
    await search_orchestrator.query_processor.close()