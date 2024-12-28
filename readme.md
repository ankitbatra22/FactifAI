# FactifAI - AI-Powered Research Assistant

FactifAI is an intelligent research assistant that combines academic papers and web results to provide comprehensive, research-backed answers to your questions. It uses advanced language models and semantic search powered by RAG (Retrieval-Augmented Generation) to deliver relevant, academically-grounded responses.

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
The `SearchOrchestrator` coordinates the entire search and response generation process:
- Manages query processing and validation
- Coordinates parallel searches across different sources
- Aggregates and ranks results
- Handles response generation

#### 2. LLM Service
Manages interactions with OpenAI's GPT-4:
- Query enhancement and reformulation
- Research summary generation
- Key findings extraction
- Response synthesis

#### 3. Vector Search Service
Powered by Pinecone and SPECTER:
- Semantic paper search
- Embedding generation
- Similar paper recommendations
- Research clustering

#### 4. Web Search Service
Custom Google Search integration:
- Filtered web results
- Source validation
- Content extraction
- Citation tracking

### Key Features

- **Rate Limiting**: 10 requests per hour per IP (currently free user)
- **CORS Support**: Configurable origins
- **Async Processing**: Parallel search execution for performance 
- **Error Handling**: Graceful degradation

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
  "web_summary": {
    "summary": "...",
    "findings": [...]
  },
  "is_valid": true
}
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
