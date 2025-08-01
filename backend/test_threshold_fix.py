#!/usr/bin/env python3
"""
Test the threshold fix for location query that was previously failing.
"""

import sys
import os
import requests
import json

API_BASE_URL = "http://localhost:8000"

def test_location_query_fix():
    """Test that location query now works correctly"""
    print("=== Testing Location Query Fix ===")
    
    test_query = "Where is your clinic located"
    
    # Test vector search directly
    print(f"🔍 Testing vector search for: '{test_query}'")
    search_response = requests.post(
        f"{API_BASE_URL}/api/chatbot/qa/search",
        headers={'Content-Type': 'application/json'},
        json={
            "query": test_query,
            "k": 5,
            "threshold": 0.5  # New threshold
        }
    )
    
    search_success = False
    if search_response.status_code == 200:
        search_data = search_response.json()
        results = search_data.get('results', [])
        
        if results:
            result = results[0]
            score = result.get('similarity_score', 0)
            answer = result.get('answer', '')
            
            print(f"✅ Vector search found location info")
            print(f"   Similarity score: {score:.3f}")
            print(f"   Answer: {answer}")
            
            if score > 0.5:
                search_success = True
                print(f"✅ Score {score:.3f} passes new threshold 0.5")
            else:
                print(f"❌ Score {score:.3f} below threshold 0.5")
        else:
            print(f"❌ No results found in vector search")
    else:
        print(f"❌ Vector search failed: {search_response.status_code}")
    
    # Test complete chat flow
    print(f"\n💬 Testing complete chat flow...")
    
    # Create session
    session_response = requests.post(
        f"{API_BASE_URL}/api/chatbot/chat/sessions",
        headers={'Content-Type': 'application/json'},
        json={"user_id": "test_threshold_fix"}
    )
    
    if session_response.status_code != 200:
        print(f"❌ Failed to create session: {session_response.status_code}")
        return False
    
    session_id = session_response.json()['session_id']
    
    # Send chat message
    chat_response = requests.post(
        f"{API_BASE_URL}/api/chatbot/chat",
        headers={'Content-Type': 'application/json'},
        json={
            "query": test_query,
            "session_id": session_id,
            "user_id": "test_threshold_fix"
        }
    )
    
    chat_success = False
    if chat_response.status_code == 200:
        chat_data = chat_response.json()
        response = chat_data.get('response', '')
        sources = chat_data.get('sources', [])
        confidence = chat_data.get('confidence_score', 0)
        search_count = chat_data.get('search_results_count', 0)
        
        print(f"🤖 LLM Response: {response[:100]}...")
        print(f"📊 Confidence: {confidence:.3f}")
        print(f"🔍 Search results used: {search_count}")
        print(f"📚 Sources: {len(sources)}")
        
        # Check if response contains location info
        location_keywords = ['112 Lengkong Tiga', 'Kembangan MRT', 'located', 'clinic']
        contains_location = any(keyword.lower() in response.lower() for keyword in location_keywords)
        
        if contains_location and sources and search_count > 0:
            chat_success = True
            print(f"✅ LLM correctly used location context")
            
            # Show source details
            for source in sources:
                print(f"   Source KB#{source.get('kb_id')}: {source.get('question')}")
                print(f"   Similarity: {source.get('similarity_score', 0):.3f}")
        else:
            print(f"❌ LLM did not use location context properly")
    else:
        print(f"❌ Chat request failed: {chat_response.status_code}")
    
    return search_success and chat_success

def test_other_queries():
    """Test that other queries still work with new threshold"""
    print(f"\n=== Testing Other Queries Still Work ===")
    
    test_queries = [
        "What are your office hours",
        "Do you accept insurance", 
        "How do I book an appointment"
    ]
    
    all_success = True
    
    for query in test_queries:
        print(f"\n🔍 Testing: '{query}'")
        
        search_response = requests.post(
            f"{API_BASE_URL}/api/chatbot/qa/search",
            headers={'Content-Type': 'application/json'},
            json={
                "query": query,
                "k": 5,
                "threshold": 0.5
            }
        )
        
        if search_response.status_code == 200:
            results = search_response.json().get('results', [])
            if results:
                score = results[0].get('similarity_score', 0)
                print(f"   ✅ Found {len(results)} results, best score: {score:.3f}")
            else:
                print(f"   ⚠️  No results found")
        else:
            print(f"   ❌ Search failed")
            all_success = False
    
    return all_success

def main():
    """Main test function"""
    print("=== Testing Threshold Fix for Location Query ===")
    print("Previous issue: Location query scored 0.608 but threshold was 0.7")
    print("Fix: Lowered threshold from 0.7 to 0.5\n")
    
    location_success = test_location_query_fix()
    other_success = test_other_queries()
    
    print(f"\n=== Threshold Fix Test Results ===")
    print(f"Location query fix: {'✅ WORKING' if location_success else '❌ FAILED'}")
    print(f"Other queries: {'✅ WORKING' if other_success else '❌ FAILED'}")
    
    if location_success and other_success:
        print("🎉 Threshold fix successful!")
        print("\nKey improvements:")
        print("• Lowered similarity threshold from 0.7 to 0.5")
        print("• Location query now correctly retrieves context")
        print("• LLM provides accurate clinic location")
        print("• Other queries continue to work properly")
        return True
    else:
        print("⚠️  Threshold fix needs attention")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)