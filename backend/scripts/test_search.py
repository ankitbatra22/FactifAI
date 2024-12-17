import asyncio
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()

from app.services.search import SearchService

async def main():
    search_service = SearchService()
    
    # Test queries
    queries = [
        "Do cows form friendships?",
        "How do cattle socialize?",
        "bovine social behavior research"
    ]
    
    for query in queries:
        print(f"\nSearching for: {query}")
        results = await search_service.search(query)
        
        print("\nResults:")
        for i, paper in enumerate(results, 1):
            print(f"\n{i}. {paper.title}")
            print(f"Confidence: {paper.confidence:.2f}")
            print(f"Summary: {paper.summary[:200]}...")

if __name__ == "__main__":
    asyncio.run(main())