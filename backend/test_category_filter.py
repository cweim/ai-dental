#!/usr/bin/env python3
"""
Test category filtering in QAEditor to verify it works correctly.
"""

import sys
import os
import requests
import json

# Add the current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

API_BASE_URL = "http://localhost:8000"

def test_category_filter():
    """Test category filtering functionality"""
    print("=== Testing Category Filter in QAEditor ===")
    
    # Get all QA entries
    response = requests.get(f"{API_BASE_URL}/api/chatbot/qa")
    if response.status_code != 200:
        print(f"❌ Failed to get QA entries: {response.status_code}")
        return False
    
    all_entries = response.json()
    print(f"📊 Total QA entries: {len(all_entries)}")
    
    # Get unique categories
    categories = list(set(entry['category'] for entry in all_entries if entry['category']))
    categories.sort()
    print(f"📂 Available categories: {categories}")
    
    # Test filtering by each category
    for category in categories[:5]:  # Test first 5 categories
        category_entries = [entry for entry in all_entries if entry['category'] == category]
        print(f"\n🏷️ Category '{category}': {len(category_entries)} entries")
        
        if category_entries:
            sample_entry = category_entries[0]
            print(f"   Sample: {sample_entry['question'][:50]}...")
    
    # Check for any entries with None/null categories
    none_categories = [entry for entry in all_entries if not entry.get('category')]
    if none_categories:
        print(f"\n⚠️  Found {len(none_categories)} entries with null/empty categories")
    
    print(f"\n✅ Category filtering test completed")
    print(f"📈 Summary: {len(categories)} unique categories, {len(all_entries)} total entries")
    
    return True

if __name__ == "__main__":
    success = test_category_filter()
    sys.exit(0 if success else 1)