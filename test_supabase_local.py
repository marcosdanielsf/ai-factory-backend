#!/usr/bin/env python3
"""
Test Supabase connection locally
"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

# Test with both variable names
url = os.getenv('SUPABASE_URL')
key_service = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
key_legacy = os.getenv('SUPABASE_KEY')

print(f"SUPABASE_URL: {url[:30]}..." if url else "SUPABASE_URL: NOT SET")
print(f"SUPABASE_SERVICE_ROLE_KEY: {'SET' if key_service else 'NOT SET'}")
print(f"SUPABASE_KEY: {'SET' if key_legacy else 'NOT SET'}")

key = key_service or key_legacy

if not url or not key:
    print("\n❌ Missing credentials!")
    exit(1)

print(f"\nUsing key: SUPABASE_{'SERVICE_ROLE_KEY' if key_service else 'KEY'}")

try:
    client = create_client(url, key)
    print("✅ Client created successfully")

    # Test query
    result = client.table('agent_versions').select('id').limit(1).execute()
    print(f"✅ Query successful! Found {len(result.data)} records")
    print(f"   Response: {result.data}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
