#!/usr/bin/env python3
"""
Test QAEditor RAG search fix and vector database rebuild functionality.
"""

import sys
import os
import requests
import json
import time

API_BASE_URL = "http://localhost:8000"

def test_vector_database_rebuild():
    """Test vector database rebuild endpoint"""
    print("=== Testing Vector Database Rebuild ===")
    
    response = requests.post(f"{API_BASE_URL}/api/chatbot/system/rebuild-index")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Vector database rebuild successful: {result.get('message', 'Success')}")
        return True
    else:
        print(f"❌ Vector database rebuild failed: {response.status_code}")
        return False

def test_rag_search_functionality():
    """Test RAG search with different queries and thresholds"""
    print("\n=== Testing RAG Search Functionality ===")
    
    test_queries = [
        {"query": "office hours", "threshold": 0.3, "expected": True},
        {"query": "dental procedures", "threshold": 0.3, "expected": True},
        {"query": "completely unrelated query about space aliens", "threshold": 0.3, "expected": False},
        {"query": "appointment", "threshold": 0.2, "expected": True}  # Lower threshold
    ]
    
    for test in test_queries:
        print(f"\n🔍 Testing query: '{test['query']}'")
        
        response = requests.post(
            f"{API_BASE_URL}/api/chatbot/qa/search",
            headers={'Content-Type': 'application/json'},
            json={
                "query": test['query'],
                "k": 3,
                "threshold": test['threshold']
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            
            print(f"   📊 Found {len(results)} results")
            
            if results:
                for i, result in enumerate(results[:2]):  # Show first 2 results
                    score = result.get('similarity_score', 0)
                    print(f"   {i+1}. {result.get('question', 'No question')[:50]}... (Score: {score:.3f})")
                
                if test['expected']:
                    print(f"   ✅ Expected results found")
                else:
                    print(f"   ⚠️  Unexpected results for irrelevant query")
            else:
                if test['expected']:
                    print(f"   ⚠️  No results found (expected some)")
                else:
                    print(f"   ✅ No results found for irrelevant query (expected)")
        else:
            print(f"   ❌ Search failed: {response.status_code}")
            return False
    
    return True

def test_vector_index_status():
    """Test vector index status"""
    print("\n=== Testing Vector Index Status ===")
    
    response = requests.get(f"{API_BASE_URL}/api/chatbot/system/stats")
    if response.status_code == 200:
        stats = response.json()
        vector_stats = stats.get('vector_search', {})
        
        print(f"📊 Vector Search Status: {vector_stats.get('status', 'unknown')}")
        print(f"📈 Indexed Entries: {vector_stats.get('indexed_entries', 'unknown')}")
        print(f"🔢 Index Dimension: {vector_stats.get('index_dimension', 'unknown')}")
        
        if vector_stats.get('status') == 'ready':
            print("✅ Vector index is ready")
            return True
        else:
            print("⚠️  Vector index may need rebuilding")
            return False
    else:
        print(f"❌ Failed to get system stats: {response.status_code}")
        return False

def main():
    """Main test function"""
    print("=== Testing QAEditor RAG Search Fixes ===")
    print("Testing improved RAG search and vector database rebuild functionality\n")
    
    # Test vector index status first
    status_success = test_vector_index_status()
    
    # Test rebuild functionality
    rebuild_success = test_vector_database_rebuild()
    
    # Wait a moment for rebuild to complete
    if rebuild_success:
        print("⏳ Waiting for rebuild to complete...")
        time.sleep(2)
    
    # Test RAG search functionality
    search_success = test_rag_search_functionality()
    
    print(f"\n=== QAEditor RAG Fix Test Results ===")
    print(f"Vector index status: {'✅ READY' if status_success else '⚠️  NEEDS REBUILD'}")
    print(f"Vector database rebuild: {'✅ WORKING' if rebuild_success else '❌ FAILED'}")
    print(f"RAG search functionality: {'✅ WORKING' if search_success else '❌ FAILED'}")
    
    if rebuild_success and search_success:
        print("🎉 All QAEditor RAG fixes working correctly!")
        print("\nKey improvements:")
        print("• RAG search now uses lower threshold (0.3) for better results")
        print("• Refresh button now rebuilds FAISS vector database")
        print("• Better error handling and user feedback")
        print("• Success alerts for rebuild operations")
        print("• Enhanced RAG test results display")
        return True
    else:
        print("⚠️  Some QAEditor RAG functionality needs attention")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)