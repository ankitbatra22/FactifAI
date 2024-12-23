import asyncio
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()

from app.services.ingestion.ingestion import IngestionService

# Sample research papers about cow social behavior
sample_papers = [
    {
        "id": "paper1",
        "title": "Social Bonds in Cattle: Evidence for Emotional Connections",
        "abstract": "This study demonstrates that cattle form strong emotional bonds with other herd members. Through behavioral observations and physiological measurements, we found evidence of stress responses when bonded pairs were separated.",
        "url": "https://example.com/paper1"
    },
    {
        "id": "paper2",
        "title": "Understanding Bovine Social Networks",
        "abstract": "Analysis of cattle social networks reveals complex relationships and hierarchies. This research shows that cows maintain consistent friendships over extended periods.",
        "url": "https://example.com/paper2"
    }
]

async def main():
    ingestion_service = IngestionService()
    
    for paper in sample_papers:
        print(f"Ingesting: {paper['title']}")
        success = await ingestion_service.ingest_paper(paper)
        if success:
            print("✓ Success")
        else:
            print("✗ Failed")

if __name__ == "__main__":
    asyncio.run(main())