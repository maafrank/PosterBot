#!/usr/bin/env python3
"""
TikTok OAuth Authentication Script
Handles the OAuth flow to get access and refresh tokens for TikTok API
"""

import os
import webbrowser
import requests
from urllib.parse import urlencode
from dotenv import load_dotenv, set_key

# Load environment variables
load_dotenv()

# TikTok API endpoints
AUTH_URL = "https://www.tiktok.com/v2/auth/authorize/"
TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"

# Configuration from .env
CLIENT_KEY = os.getenv("TIKTOK_CLIENT_KEY")
CLIENT_SECRET = os.getenv("TIKTOK_CLIENT_SECRET")
REDIRECT_URI = os.getenv("TIKTOK_REDIRECT_URI")

def generate_auth_url():
    """Generate the TikTok authorization URL"""
    params = {
        "client_key": CLIENT_KEY,
        "scope": "user.info.basic,video.publish",
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "state": "posterbot_auth"  # Optional state parameter for security
    }

    auth_url = f"{AUTH_URL}?{urlencode(params)}"
    return auth_url

def exchange_code_for_tokens(auth_code):
    """Exchange authorization code for access and refresh tokens"""

    data = {
        "client_key": CLIENT_KEY,
        "client_secret": CLIENT_SECRET,
        "code": auth_code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cache-Control": "no-cache"
    }

    try:
        response = requests.post(TOKEN_URL, data=data, headers=headers)
        response.raise_for_status()

        result = response.json()

        # TikTok returns tokens directly in the response, not wrapped in "data"
        if "access_token" in result:
            return result
        elif "data" in result:
            return result["data"]
        elif "error" in result:
            print(f"❌ Error from TikTok: {result['error']}")
            if "error_description" in result:
                print(f"   Description: {result['error_description']}")
            return None
        else:
            print(f"❌ Unexpected response format: {result}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Response: {e.response.text}")
        return None

def save_tokens_to_env(access_token, refresh_token, expires_in):
    """Save tokens to .env file"""
    env_file = ".env"

    try:
        set_key(env_file, "TIKTOK_ACCESS_TOKEN", access_token)
        set_key(env_file, "TIKTOK_REFRESH_TOKEN", refresh_token)
        print(f"✅ Tokens saved to {env_file}")
        print(f"   Access token expires in {expires_in} seconds ({expires_in // 3600} hours)")
        return True
    except Exception as e:
        print(f"❌ Failed to save tokens: {e}")
        return False

def main():
    """Main OAuth flow"""
    print("=" * 60)
    print("PosterBot - TikTok OAuth Authentication")
    print("=" * 60)
    print()

    # Validate configuration
    if not CLIENT_KEY or not CLIENT_SECRET or not REDIRECT_URI:
        print("❌ Missing TikTok configuration in .env file")
        print("   Please ensure TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET,")
        print("   and TIKTOK_REDIRECT_URI are set.")
        return

    print("Configuration:")
    print(f"  Client Key: {CLIENT_KEY}")
    print(f"  Redirect URI: {REDIRECT_URI}")
    print()

    # Generate authorization URL
    auth_url = generate_auth_url()

    print("Step 1: Authorize PosterBot with TikTok")
    print("-" * 60)
    print("Opening authorization page in your browser...")
    print()
    print("If it doesn't open automatically, visit this URL:")
    print(auth_url)
    print()

    # Open browser
    try:
        webbrowser.open(auth_url)
    except Exception as e:
        print(f"⚠️  Could not open browser automatically: {e}")

    print("Step 2: Authorize and Get Code")
    print("-" * 60)
    print("1. Log into TikTok and click 'Authorize'")
    print("2. You'll be redirected to the callback page")
    print("3. Copy the authorization code displayed")
    print()

    # Get authorization code from user
    auth_code = input("Paste the authorization code here: ").strip()

    if not auth_code:
        print("❌ No authorization code provided. Exiting.")
        return

    print()
    print("Step 3: Exchange Code for Tokens")
    print("-" * 60)
    print("Requesting access token from TikTok...")

    # Exchange code for tokens
    token_data = exchange_code_for_tokens(auth_code)

    if not token_data:
        print("❌ Failed to get tokens. Please try again.")
        return

    # Extract token information
    access_token = token_data.get("access_token")
    refresh_token = token_data.get("refresh_token")
    expires_in = token_data.get("expires_in")
    token_type = token_data.get("token_type")
    scope = token_data.get("scope")

    if not access_token or not refresh_token:
        print("❌ Response missing required tokens")
        print(f"   Response data: {token_data}")
        return

    print("✅ Successfully received tokens!")
    print(f"   Token type: {token_type}")
    print(f"   Scopes: {scope}")
    print()

    # Save to .env file
    print("Step 4: Save Tokens")
    print("-" * 60)

    if save_tokens_to_env(access_token, refresh_token, expires_in):
        print()
        print("=" * 60)
        print("✅ Authentication Complete!")
        print("=" * 60)
        print()
        print("You can now use PosterBot to post videos to TikTok!")
        print("Run: python3 main.py --distribute tiktok")
        print()
        print("⚠️  Note: Access tokens expire. If you get authentication")
        print("   errors in the future, run this script again.")
    else:
        print()
        print("⚠️  Authentication succeeded but failed to save tokens.")
        print("   Please manually add these to your .env file:")
        print(f"   TIKTOK_ACCESS_TOKEN={access_token}")
        print(f"   TIKTOK_REFRESH_TOKEN={refresh_token}")

if __name__ == "__main__":
    main()
