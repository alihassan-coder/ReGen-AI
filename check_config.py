#!/usr/bin/env python3
"""
Configuration validation script for ReGenAI Backend
Run this before starting the server to verify your setup
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_env_var(name, required=True):
    """Check if an environment variable is set"""
    value = os.getenv(name)
    if value:
        # Mask sensitive values
        if 'KEY' in name or 'SECRET' in name or 'PASSWORD' in name:
            display = value[:10] + '...' if len(value) > 10 else '***'
        else:
            display = value[:50] + '...' if len(value) > 50 else value
        print(f"✅ {name}: {display}")
        return True
    else:
        if required:
            print(f"❌ {name}: NOT SET (REQUIRED)")
        else:
            print(f"⚠️  {name}: Not set (optional)")
        return not required

def main():
    print("=" * 60)
    print("ReGenAI Backend Configuration Check")
    print("=" * 60)
    print()
    
    all_good = True
    
    # Database
    print("📊 Database Configuration:")
    db_url = check_env_var("DATABASE_URL", required=False)
    neon_url = check_env_var("NEON_DATABASE_URL", required=False)
    if not (db_url or neon_url):
        print("❌ ERROR: At least one database URL is required!")
        all_good = False
    print()
    
    # AI Model
    print("🤖 AI Model Configuration:")
    gemini = check_env_var("GEMINI_API_KEY_ALI", required=True)
    if not gemini:
        print("   Get your key from: https://makersuite.google.com/app/apikey")
        all_good = False
    check_env_var("OPENAI_API_KEY", required=False)
    print()
    
    # Authentication
    print("🔐 Authentication Configuration:")
    secret = check_env_var("SECRET_KEY", required=False)
    if not secret:
        print("   ⚠️  WARNING: Using default SECRET_KEY is insecure!")
        print("   Generate a secure key: python -c 'import secrets; print(secrets.token_urlsafe(32))'")
    print()
    
    # Optional APIs
    print("🌤️  Optional APIs:")
    check_env_var("OPENWEATHER_API_KEY", required=False)
    check_env_var("AIRVISUAL_API_KEY", required=False)
    print()
    
    # Summary
    print("=" * 60)
    if all_good:
        print("✅ Configuration looks good! You can start the server.")
        print()
        print("Start with: uvicorn main:app --reload --port 8000")
        return 0
    else:
        print("❌ Configuration has issues. Please fix them before starting.")
        print()
        print("Steps:")
        print("1. Copy .env.example to .env")
        print("2. Edit .env and add your credentials")
        print("3. Run this script again to verify")
        return 1

if __name__ == "__main__":
    sys.exit(main())
