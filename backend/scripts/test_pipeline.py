import asyncio
import sys
import os
from datetime import datetime
import aiohttp

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.ingestion.pipeline import SearchPipeline
from dotenv import load_dotenv

load_dotenv()

async def main():
    print("\n=== Testing Full Pipeline with Real APIs ===")
    
    # Initialize pipeline
    print("Initializing pipeline...")
    pipeline = SearchPipeline()
    
    # Test query
    query = "can cows make friends?"
    print(f"\nSearching for: {query}")
    
    try:
        # Set a timeout for the entire operation
        async with asyncio.timeout(30):  # 30 second timeout
            start_time = datetime.now()
            
            # Get results
            print("\nFetching and ranking papers...")
            results = await pipeline.search(query, top_k=5)
            
            # Display results
            print(f"\nFound {len(results)} relevant papers in {datetime.now() - start_time}:")
            print("-" * 80)
            
            for i, result in enumerate(results, 1):
                print(f"\n{i}. Title: {result['title']}")
                print(f"Source: {result['source']}")
                print(f"Score: {result['score']:.3f}")
                print(f"URL: {result['url']}")
                print(f"Content Preview: {result['content'][:200]}...")
                print("-" * 80)
            
    except asyncio.TimeoutError:
        print("Pipeline execution timed out after 30 seconds")
    except Exception as e:
        print(f"Error during pipeline execution: {str(e)}")
        raise
    finally:
        # Close any remaining sessions
        for task in asyncio.all_tasks():
            if not task.done():
                task.cancel()
        
        # Close aiohttp sessions
        for attr in dir(pipeline):
            obj = getattr(pipeline, attr)
            if isinstance(obj, aiohttp.ClientSession):
                await obj.close()
        
        # Close sessions in connectors
        for connector in pipeline.sources.values():
            if hasattr(connector, 'session') and isinstance(connector.session, aiohttp.ClientSession):
                await connector.session.close()

if __name__ == "__main__":
    asyncio.run(main()) 