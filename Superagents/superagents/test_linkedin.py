"""Test LinkedIn API access"""
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

async def test_linkedin():
    import httpx
    
    token = os.getenv('LINKEDIN_ACCESS_TOKEN')
    if not token:
        print("No LinkedIn token found!")
        return
    
    print(f"LinkedIn Token: {token[:20]}...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }
    
    async with httpx.AsyncClient(timeout=30) as client:
        # Test 1: Get your own profile
        print("\n1. Testing /me endpoint...")
        resp = await client.get(
            "https://api.linkedin.com/v2/me",
            headers=headers
        )
        print(f"   Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"   Profile: {data.get('localizedFirstName', '')} {data.get('localizedLastName', '')}")
        else:
            print(f"   Error: {resp.text[:200]}")
        
        # Test 2: Check email access
        print("\n2. Testing email endpoint...")
        resp = await client.get(
            "https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))",
            headers=headers
        )
        print(f"   Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            elements = data.get("elements", [])
            if elements:
                email = elements[0].get("handle~", {}).get("emailAddress", "")
                print(f"   Email: {email}")
        else:
            print(f"   Error: {resp.text[:200]}")
        
        # Test 3: Check organization access
        print("\n3. Testing organization access...")
        resp = await client.get(
            "https://api.linkedin.com/v2/organizationalEntityAcls?q=roleAssignee",
            headers=headers
        )
        print(f"   Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"   Organizations: {len(data.get('elements', []))} found")
        else:
            print(f"   Error: {resp.text[:200]}")
        
        # Test 4: Check connections
        print("\n4. Testing connections access...")
        resp = await client.get(
            "https://api.linkedin.com/v2/connections?q=viewer&start=0&count=5",
            headers=headers
        )
        print(f"   Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"   Connections available")
        else:
            print(f"   Error: {resp.text[:150]}")

if __name__ == "__main__":
    asyncio.run(test_linkedin())
