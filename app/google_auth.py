"""
Google OAuth2 One-Time Authentication Script
============================================
Run this script ONCE from your terminal after setting up your Google Cloud project
to generate the `token.json` file that grants the agents access to your Google account.

Usage:
    python app/google_auth.py

Requirements:
    1. Download your OAuth 2.0 credentials from Google Cloud Console
       (APIs & Services → Credentials → OAuth 2.0 Client IDs → Download JSON)
    2. Save the file as `credentials.json` in the project root
    3. Ensure GOOGLE_CREDENTIALS_PATH is set in your .env (or defaults to 'credentials.json')
    4. Run this script — a browser window will open for you to authorize
    5. After authorizing, `token.json` is created automatically
"""

import os
from dotenv import load_dotenv
load_dotenv()

CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")
TOKEN_PATH       = os.getenv("GOOGLE_TOKEN_PATH", "token.json")

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
]

if __name__ == "__main__":
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.oauth2.credentials import Credentials

        if not os.path.exists(CREDENTIALS_PATH):
            print(f"❌ '{CREDENTIALS_PATH}' not found.")
            print("   Please download your OAuth 2.0 credentials from Google Cloud Console")
            print("   and save them as 'credentials.json' in the project root.")
            exit(1)

        print("🔐 Starting Google OAuth2 authentication flow...")
        print("   A browser window will open. Log in and grant the requested permissions.\n")

        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
        creds = flow.run_local_server(port=0)

        with open(TOKEN_PATH, "w") as token_file:
            token_file.write(creds.to_json())

        print(f"\n✅ Authentication successful! Token saved to '{TOKEN_PATH}'")
        print("   Your Executive Assistant Agent can now access your Google Calendar and Gmail.")

    except ImportError:
        print("❌ Missing dependencies. Run: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
