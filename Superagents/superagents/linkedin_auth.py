"""
LinkedIn OAuth Token Generator
Run this script, follow the URL, and paste the code you get back.
"""
import webbrowser
import urllib.parse
import httpx
import os

# Your LinkedIn App Credentials
CLIENT_ID = "86xzcfcfqbcet4"
CLIENT_SECRET = "WPL_AP1.pMcD1MufsT4HGajI.bGgw/Q=="
REDIRECT_URI = "https://localhost:8080/callback"  # Must match app settings

# Scopes needed for prospecting
# Note: Some scopes require LinkedIn app review/approval
SCOPES = [
    "openid",             # Basic OpenID (usually available)
    "profile",            # Read basic profile
    # "r_liteprofile",    # Requires approval
    # "r_emailaddress",   # Requires approval  
    # "w_member_social",  # Requires approval
]

def get_auth_url():
    """Generate LinkedIn authorization URL"""
    base_url = "https://www.linkedin.com/oauth/v2/authorization"
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": " ".join(SCOPES),
        "state": "superagent_auth"
    }
    return f"{base_url}?{urllib.parse.urlencode(params)}"

def exchange_code_for_token(auth_code: str) -> dict:
    """Exchange authorization code for access token"""
    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    
    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    
    response = httpx.post(token_url, data=data)
    return response.json()

def main():
    print("=" * 60)
    print("LinkedIn OAuth Token Generator")
    print("=" * 60)
    
    auth_url = get_auth_url()
    
    print("\nStep 1: Open this URL in your browser:")
    print("-" * 60)
    print(auth_url)
    print("-" * 60)
    
    print("\nStep 2: Log in to LinkedIn and authorize the app")
    print("\nStep 3: You'll be redirected to a URL like:")
    print("   https://localhost:8080/callback?code=XXXXXX&state=superagent_auth")
    print("\n   (The page won't load - that's OK! Just copy the 'code' value)")
    
    # Try to open browser automatically
    try:
        webbrowser.open(auth_url)
        print("\n[Browser opened automatically]")
    except:
        print("\n[Copy the URL above and paste in your browser]")
    
    print("\n" + "=" * 60)
    auth_code = input("Paste the authorization code here: ").strip()
    
    # Clean up the code - user might paste full URL or "code=xxx"
    if "code=" in auth_code:
        import re
        match = re.search(r'code=([^&]+)', auth_code)
        if match:
            auth_code = match.group(1)
    
    if not auth_code:
        print("No code entered. Exiting.")
        return
    
    print("\nExchanging code for access token...")
    result = exchange_code_for_token(auth_code)
    
    if "access_token" in result:
        token = result["access_token"]
        expires_in = result.get("expires_in", 0)
        
        print("\n" + "=" * 60)
        print("SUCCESS! Here's your access token:")
        print("=" * 60)
        print(token)
        print("=" * 60)
        print(f"\nExpires in: {expires_in // 86400} days")
        
        # Offer to save to .env
        save = input("\nSave to .env files? (y/n): ").strip().lower()
        if save == 'y':
            # Update both .env files
            for env_path in ["F:/Superagents/superagents/.env", "C:/Superagents/superagents/.env"]:
                try:
                    with open(env_path, 'r') as f:
                        content = f.read()
                    
                    # Replace LinkedIn token line
                    import re
                    new_content = re.sub(
                        r'LINKEDIN_ACCESS_TOKEN=.*',
                        f'LINKEDIN_ACCESS_TOKEN={token}',
                        content
                    )
                    
                    with open(env_path, 'w') as f:
                        f.write(new_content)
                    
                    print(f"  ✓ Updated {env_path}")
                except Exception as e:
                    print(f"  ✗ Failed to update {env_path}: {e}")
        
        print("\nDone! Run test_linkedin.py to verify.")
    else:
        print("\n" + "=" * 60)
        print("ERROR: Could not get access token")
        print("=" * 60)
        print(result)
        
        if "error_description" in result:
            print(f"\nReason: {result['error_description']}")

if __name__ == "__main__":
    main()
