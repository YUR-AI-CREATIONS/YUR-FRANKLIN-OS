"""Test the site auditor"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.site_auditor import SiteAuditor

async def main():
    auditor = SiteAuditor()
    
    # Test with real sites
    test_sites = ["google.com", "yur-ai.com"]
    
    for site in test_sites:
        print(f"\n{'='*50}")
        print(f"Auditing {site}...")
        result = await auditor.audit_site(site)
        
        print(f"\nScore: {result['score']}/100")
        print(f"Load time: {result['load_time_ms']}ms")
        print(f"SSL Valid: {result['ssl_valid']}")
        print(f"Industry: {result['industry_hints']}")
        print(f"\nIssues ({len(result['issues'])}):")
        for issue in result['issues'][:5]:  # First 5
            print(f"  [{issue['type'].upper()}] {issue['message']}")
        print(f"\nRecommendation: {result['recommendation']}")
    
    await auditor.close()

if __name__ == "__main__":
    asyncio.run(main())
