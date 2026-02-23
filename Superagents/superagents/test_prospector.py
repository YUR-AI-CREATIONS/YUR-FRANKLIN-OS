"""Test full prospecting: Apollo (companies) + Hunter (emails)"""
import asyncio
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv
load_dotenv()

async def test_full_prospecting():
    from agents.prospector import LinkedInProspector
    
    print("=" * 60)
    print("Full Prospecting Test: Apollo + Hunter.io")
    print("=" * 60)
    
    prospector = LinkedInProspector()
    
    # Step 1: Find companies via Apollo
    print("\n[1] Finding fintech companies via Apollo...")
    companies = await prospector.find_prospects(
        industry="fintech",
        company_size="20-500",
        limit=3
    )
    
    if not companies:
        print("    No companies found!")
        await prospector.close()
        return
    
    print(f"    Found {len(companies)} companies")
    
    # Step 2: For each company, find contacts via Hunter
    print("\n[2] Finding contacts via Hunter.io...")
    
    total_contacts = 0
    for company in companies:
        domain = company.get("domain", "")
        name = company.get("name", "")
        
        if not domain:
            print(f"    - {name}: No domain, skipping")
            continue
        
        print(f"\n    {name} ({domain}):")
        contacts = await prospector.get_decision_makers(domain)
        
        if contacts:
            total_contacts += len(contacts)
            for c in contacts[:3]:  # Show first 3
                print(f"      → {c.get('name', 'Unknown')} | {c.get('title', 'N/A')} | {c.get('email', 'no email')}")
        else:
            print(f"      No contacts found")
    
    print("\n" + "=" * 60)
    print(f"TOTAL: {len(companies)} companies, {total_contacts} contacts with emails")
    print("=" * 60)
    
    await prospector.close()

if __name__ == "__main__":
    asyncio.run(test_full_prospecting())
