#!/usr/bin/env python3
"""
Bootstrap script to authenticate with Google OAuth locally.
Run this script on your local machine to generate token.pickle,
then upload that file to your Replit project.

Usage:
1. Download client_secret.json to your local machine
2. Run: python auth_bootstrap.py
3. Follow the browser authentication
4. Upload the generated token.pickle to your Replit project
"""

import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

def main():
    print("🔐 YouTube API Authentication Bootstrap")
    print("=" * 50)
    
    try:
        # Run local OAuth flow with browser
        flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
        creds = flow.run_local_server(port=0)
        
        # Save credentials for future use
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
            
        print("✅ Authentication successful!")
        print("📁 Generated: token.pickle")
        print("\n📋 Next steps:")
        print("1. Upload token.pickle to your Replit project")
        print("2. Run your YouTube monitor script")
        print("\n🔒 Keep token.pickle secure - it contains your YouTube access credentials!")
        
    except FileNotFoundError:
        print("❌ Error: client_secret.json not found")
        print("Please download your Google OAuth credentials file as 'client_secret.json'")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")

if __name__ == "__main__":
    main()