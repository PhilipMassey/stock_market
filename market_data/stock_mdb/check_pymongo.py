#!/usr/bin/env python3
"""
Test script to debug MongoDB connection issue
Run this from the same directory as your app.py
"""

import sys
import traceback

print("=" * 60)
print("Testing MongoDB Connection")
print("=" * 60)

# Test 1: Basic pymongo connection
print("\n1. Testing basic pymongo connection...")
try:
    from pymongo import MongoClient
    client = MongoClient()
    db = client['stock_market']
    print("✓ Basic connection successful")
    print(f"  Database: {db}")
except Exception as e:
    print(f"✗ Basic connection failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 2: Import the apis module
print("\n2. Testing import of apis module...")
try:
    # Add the path if needed
    sys.path.insert(0, '/Users/philipmassey/stock_market')
    import apis.seeking_alpha.symbol_financial_info.mdb_in_out as mdb_in_out
    print("✓ Module import successful")
except Exception as e:
    print(f"✗ Module import failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 3: Call the get_sectors_industry function
print("\n3. Testing get_sectors_industry() function...")
try:
    result = mdb_in_out.get_sectors_industry()
    print("✓ Function call successful")
    print(f"  Result type: {type(result)}")
    if isinstance(result, list):
        print(f"  Result length: {len(result)}")
    elif isinstance(result, dict):
        print(f"  Result keys: {list(result.keys())[:5]}")
except Exception as e:
    print(f"✗ Function call failed: {e}")
    traceback.print_exc()

print("\n" + "=" * 60)
print("Diagnosis:")
print("=" * 60)
print("""
If test 1 passes but test 3 fails, the issue is likely:
- The MongoDB query in get_sectors_industry() is taking too long
- There's a connection pool issue
- The collection doesn't exist or has no data

Suggested fixes:
1. Increase MongoDB timeout in the connection string
2. Add connection pooling parameters
3. Add error handling to get_sectors_industry()
4. Lazy-load the data instead of loading at import time
""")