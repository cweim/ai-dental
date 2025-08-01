#!/usr/bin/env python3
"""
Test vector index auto-initialization fixes.
"""

import sys
import os
import requests
import json

API_BASE_URL = "http://localhost:8000"

def test_index_status_after_startup():
    """Test that index is properly initialized after application startup"""
    print("=== Testing Index Auto-Initialization ===")
    
    # Check if index is ready immediately after startup
    response = requests.get(f"{API_BASE_URL}/api/chatbot/system/stats")
    if response.status_code == 200:
        stats = response.json()
        vector_stats = stats.get('vector_search', {})
        
        status = vector_stats.get('status', 'unknown')
        entries = vector_stats.get('total_entries', 0)
        
        print(f"📊 Vector Index Status: {status}")
        print(f"📈 Index Entries: {entries}")
        
        if status == 'ready' and entries > 0:
            print("✅ Index is properly initialized on startup")
            return True
        else:
            print("❌ Index is not properly initialized")
            return False
    else:
        print(f"❌ Failed to get system stats: {response.status_code}")
        return False

def test_search_auto_initialization():
    """Test that search operations can auto-initialize if needed"""
    print(f"\n=== Testing Search Auto-Initialization ===")
    
    # Test a search operation
    test_query = "What are your office hours"
    
    response = requests.post(
        f"{API_BASE_URL}/api/chatbot/qa/search",
        headers={'Content-Type': 'application/json'},
        json={
            "query": test_query,
            "k": 3,
            "threshold": 0.5
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        results = data.get('results', [])
        
        print(f"🔍 Search for '{test_query}' returned {len(results)} results")
        
        if results:
            print("✅ Search operation successful (index was available or auto-initialized)")
            
            # Show sample result
            sample = results[0]
            print(f"   Sample: {sample.get('question', 'No question')}")
            print(f"   Score: {sample.get('similarity_score', 0):.3f}")
            
            return True
        else:
            print("⚠️  Search returned no results (may indicate initialization issues)")
            return False
    else:
        print(f"❌ Search failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

def test_chat_flow_robustness():
    """Test that chat flow works reliably"""
    print(f"\n=== Testing Chat Flow Robustness ===")
    
    # Create session
    session_response = requests.post(
        f"{API_BASE_URL}/api/chatbot/chat/sessions",
        headers={'Content-Type': 'application/json'},
        json={"user_id": "test_robustness"}
    )
    
    if session_response.status_code != 200:
        print(f"❌ Failed to create session: {session_response.status_code}")
        return False
    
    session_id = session_response.json()['session_id']
    print(f"✅ Created session: {session_id[:8]}...")
    
    # Test multiple queries to ensure consistency
    test_queries = [
        "Where is your clinic located",
        "What are your office hours",
        "Do you accept insurance"
    ]
    
    all_successful = True
    
    for query in test_queries:
        chat_response = requests.post(
            f"{API_BASE_URL}/api/chatbot/chat",
            headers={'Content-Type': 'application/json'},
            json={
                "query": query,
                "session_id": session_id,
                "user_id": "test_robustness"
            }
        )
        
        if chat_response.status_code == 200:
            data = chat_response.json()
            response_text = data.get('response', '')
            sources = data.get('sources', [])
            search_count = data.get('search_results_count', 0)
            
            print(f"   🤖 '{query}': {len(response_text)} chars, {len(sources)} sources, {search_count} search results")
            
            if len(response_text) > 50:  # Reasonable response length
                print(f"      ✅ Good response generated")
            else:
                print(f"      ⚠️  Short response: {response_text}")
                all_successful = False
        else:
            print(f"   ❌ Chat failed for '{query}': {chat_response.status_code}")
            all_successful = False
    
    return all_successful

def create_summary_report():
    """Create a summary of the index rebuild issue and fixes"""
    print(f"\n=== Index Rebuild Issue Summary ===")
    
    print(f"🔍 PROBLEM IDENTIFIED:")
    print(f"   • Vector search index was not initialized on application startup")
    print(f"   • Each server restart left index uninitialized")
    print(f"   • Manual rebuilds were required after every restart")
    
    print(f"\n🛠️  FIXES IMPLEMENTED:")
    print(f"   1. Added vector index initialization to app startup event")
    print(f"   2. Added auto-initialization in search method as backup")
    print(f"   3. Index files are properly persisted to disk")
    print(f"   4. Comprehensive error handling and logging")
    
    print(f"\n📋 ROOT CAUSES:")
    print(f"   • Missing startup initialization in main.py")
    print(f"   • No fallback mechanism for uninitialized index")
    print(f"   • Index stored in memory but not auto-loaded")
    
    print(f"\n✅ EXPECTED BEHAVIOR NOW:")
    print(f"   • Index auto-loads from disk on startup")
    print(f"   • Search operations work immediately")
    print(f"   • No manual rebuilds needed after restarts")
    print(f"   • Graceful fallback if initialization fails")

def main():
    """Main test function"""
    print("=== Vector Index Auto-Initialization Test ===")
    print("Testing fixes for the index rebuild issue\n")
    
    startup_success = test_index_status_after_startup()
    search_success = test_search_auto_initialization()
    chat_success = test_chat_flow_robustness()
    
    create_summary_report()
    
    print(f"\n=== Test Results ===")
    print(f"Startup initialization: {'✅ WORKING' if startup_success else '❌ FAILED'}")
    print(f"Search auto-init: {'✅ WORKING' if search_success else '❌ FAILED'}")
    print(f"Chat flow robustness: {'✅ WORKING' if chat_success else '❌ FAILED'}")
    
    if startup_success and search_success and chat_success:
        print("🎉 Index auto-initialization fixes successful!")
        print("\n💡 This should eliminate the need for manual index rebuilds after server restarts")
        return True
    else:
        print("⚠️  Some fixes may need further attention")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)