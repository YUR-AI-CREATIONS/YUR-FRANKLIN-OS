"""Test the website redesign campaign pipeline"""
import asyncio
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Create a test CSV with a few sample leads
test_csv_content = """email,company,name,industry
test@outdated-site-example.com,Test Company,John Doe,general
info@yur-ai.com,Yur AI,,,technology
"""

async def test_campaign():
    from campaigns.website_redesign import WebsiteRedesignCampaign, ExpiringLinkGenerator
    
    print("=" * 60)
    print("Testing Expiring Link Generator")
    print("=" * 60)
    
    # Test link generation
    link_gen = ExpiringLinkGenerator()
    
    link = link_gen.generate_link(
        email="test@example.com",
        industry="legal",
        template_id="law-firm-modern-01",
        expires_minutes=30
    )
    print(f"Generated link: {link[:80]}...")
    
    # Verify it
    token = link.split("?token=")[1]
    result = link_gen.verify_link(token)
    print(f"Verification: {result}")
    
    # Test expired link
    expired_link = link_gen.generate_link(
        email="expired@example.com",
        industry="general",
        template_id="test-01",
        expires_minutes=-1  # Already expired
    )
    expired_token = expired_link.split("?token=")[1]
    expired_result = link_gen.verify_link(expired_token)
    print(f"Expired link check: {expired_result}")
    
    print("\n" + "=" * 60)
    print("Testing Campaign (Dry Run)")
    print("=" * 60)
    
    # Write test CSV
    test_csv_path = "test_leads.csv"
    with open(test_csv_path, "w") as f:
        f.write(test_csv_content)
    
    # Run dry campaign
    campaign = WebsiteRedesignCampaign()
    results = await campaign.run_campaign(
        csv_path=test_csv_path,
        limit=2,
        dry_run=True
    )
    
    print(f"\nResults: {results}")
    
    # Cleanup
    os.remove(test_csv_path)
    
    print("\n✓ Campaign pipeline tested successfully!")

if __name__ == "__main__":
    asyncio.run(test_campaign())
