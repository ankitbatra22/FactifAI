# FactifAI - AI-Powered Research Assistant

FactifAI is an intelligent research assistant that combines embedding search academic papers and a web result summary to provide comprehensive, research-backed answers to your questions. It uses advanced language models and semantic search powered by RAG (Retrieval-Augmented Generation) to deliver relevant, academically-grounded responses. 

Key findings are always from trusted sources to truly be able to back up your research query 🚀

## Tech Stack

### Backend
- FastAPI (Python)
- OpenAI API
- Sentence Transformers (SPECTER)
- Pinecone Vector Database

### Frontend
- Next.js 14 (React)
- TypeScript
- Tailwind CSS

## Backend Architecture

### Core Services

#### 1. Search Orchestrator
The `SearchOrchestrator` coordinates the entire search by calling the other services.
- Manages query processing and validation (catches invalid queries like "hi") (LLM Service)
- Ingests papers from sources like Arxiv, PubMed, etc. based on query (Ingestion Service/Pipeline) 
- Aggregates and ranks results (Embedding Service)
- Handles response generation (LLM Service)

#### 2. LLM Service
Manages interactions with OpenAI's GPT-4:
- Query enhancement and reformulation (E.g Turns "Can Cows Make Friends?" into "Bovine social behavior")
- Research summary generation (Uses papers and web results to generate a summary)
- Key findings extraction
- Response synthesis

#### 3. Vector Search Service
Powered by Pinecone and SPECTER:
- Semantic paper search 
- Embedding generation
- Similar paper recommendations
- Research clustering

### 4. Ingestion Pipeline
Runs runtime ingestion of academic papers from sources like Arxiv, PubMed, Crossref, and OpenAlex. (see: `app/services/ingestion/sources` for all API's being accessed) which are then used to generate embeddings and store in Pinecone to be used for semantic search/similarity search with query. 

### Additional Features
- **Caching**: Recent search storage
- **Robustness**: Query validation error handling, graceful degradation, performance monitoring, health checks
- **Security**: Rate limiting, CORS support

## Frontend Features

- **Server-Side Rendering**: Fast initial page loads
- **Client-Side Caching**: Recent search storage
- **Responsive Design**: Mobile-first approach
- **Error Handling**: User-friendly error messages
- **Loading States**: Smooth loading transitions


## API Endpoints

### `POST /search`
Main search endpoint that accepts research queries.

**Request:**
```json
{
  "query": "What are the effects of meditation on stress?"
}
```

**Response:**
```json
{
  "papers": [...],
  "summary": {
    "snippet": "...",
    "findings": [...]
  },
  "is_valid": true
}
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
