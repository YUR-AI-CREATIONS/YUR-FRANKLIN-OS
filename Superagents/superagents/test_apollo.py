"""Quick test of Apollo.io API + Prospector"""
import asyncio
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv
load_dotenv()

async def test_prospector():
    from agents.prospector import LinkedInProspector
    
    print("Testing LinkedIn Prospector with Apollo.io...")
    prospector = LinkedInProspector()
    
    # Test finding companies
    companies = await prospector.find_prospects(
        industry="fintech",
        company_size="20-500",
        limit=5
    )
    
    print(f"\nFound {len(companies)} companies:")
    for c in companies:
        print(f"  - {c.get('name')} ({c.get('domain')}) - {c.get('employee_count')} employees")
    
    await prospector.close()

if __name__ == "__main__":
    asyncio.run(test_prospector())
