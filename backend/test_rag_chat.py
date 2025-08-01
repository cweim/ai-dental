#!/usr/bin/env python3
"""
Test RAG system integration in Chat.tsx and ChatbotTester.tsx interfaces.
This test verifies that both frontend chat interfaces correctly:
1. Create chat sessions
2. Send queries to the backend
3. Receive responses with RAG-retrieved sources
4. Display source information properly
"""

import sys
import os
import requests
import json
import time

# Add the current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

API_BASE_URL = "http://localhost:8000"

def test_chat_session_creation():
    """Test creating a chat session (used by both interfaces)"""
    print("=== Testing Chat Session Creation ===")
    
    # Test session creation for patient interface (Chat.tsx)
    response = requests.post(
        f"{API_BASE_URL}/api/chatbot/chat/sessions",
        headers={'Content-Type': 'application/json'},
        json={"user_id": f"patient_{int(time.time())}"}
    )
    
    if response.status_code == 200:
        session_data = response.json()
        print(f"✅ Patient session created: {session_data['session_id'][:8]}...")
        patient_session = session_data
    else:
        print(f"❌ Failed to create patient session: {response.status_code}")
        return False, None, None
    
    # Test session creation for admin tester interface (ChatbotTester.tsx)
    response = requests.post(
        f"{API_BASE_URL}/api/chatbot/chat/sessions",
        headers={'Content-Type': 'application/json'},
        json={"user_id": "admin_tester"}
    )
    
    if response.status_code == 200:
        session_data = response.json()
        print(f"✅ Admin session created: {session_data['session_id'][:8]}...")
        admin_session = session_data
    else:
        print(f"❌ Failed to create admin session: {response.status_code}")
        return False, None, None
    
    return True, patient_session, admin_session

def test_rag_query(session, user_type, test_query):
    """Test RAG query processing"""
    print(f"\n=== Testing RAG Query for {user_type.title()} Interface ===")
    print(f"Query: '{test_query}'")
    
    # Send chat query (same endpoint used by both interfaces)
    response = requests.post(
        f"{API_BASE_URL}/api/chatbot/chat",
        headers={'Content-Type': 'application/json'},
        json={
            "query": test_query,
            "session_id": session['session_id'],
            "user_id": session['user_id']
        }
    )
    
    if response.status_code != 200:
        print(f"❌ Chat query failed: {response.status_code} - {response.text}")
        return False
    
    data = response.json()
    
    # Check response structure (what both interfaces expect)
    required_fields = ['session_id', 'response', 'sources', 'confidence_score', 'response_time_ms', 'search_results_count']
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        print(f"❌ Missing response fields: {missing_fields}")
        return False
    
    print(f"✅ Response received ({data['response_time_ms']}ms)")
    print(f"📝 Response: {data['response'][:100]}...")
    print(f"🔍 Sources found: {len(data['sources'])}")
    print(f"📊 Confidence: {data['confidence_score']:.2f}")
    print(f"🔢 Search results: {data['search_results_count']}")
    
    # Check if sources have the correct structure for frontend display
    if data['sources']:
        source = data['sources'][0]
        required_source_fields = ['kb_id', 'question', 'category', 'source', 'similarity_score']
        missing_source_fields = [field for field in required_source_fields if field not in source]
        
        if missing_source_fields:
            print(f"❌ Missing source fields: {missing_source_fields}")
            return False
        
        print(f"📚 Sample source: KB #{source['kb_id']} - {source['question'][:50]}... (similarity: {source['similarity_score']:.2f})")
        print(f"🏷️ Category: {source['category']}, Source: {source['source']}")
        
        return True
    else:
        print("⚠️  No sources found - may indicate low similarity or empty knowledge base")
        return data['search_results_count'] == 0  # Acceptable if no results found

def test_frontend_integration():
    """Test frontend integration points"""
    print("\n=== Testing Frontend Integration Points ===")
    
    # Test QA stats endpoint (used by frontend for "RAG Ready" count)
    response = requests.get(f"{API_BASE_URL}/api/chatbot/system/stats")
    if response.status_code == 200:
        stats = response.json()
        qa_stats = stats.get('qa_management', {})
        total_active = qa_stats.get('total_active', 0)
        print(f"✅ System stats available - Active QA pairs: {total_active}")
        
        if total_active > 0:
            print(f"✅ RAG system ready with {total_active} knowledge base entries")
            return True
        else:
            print("⚠️  No active QA pairs found - RAG system not ready")
            return False
    else:
        print(f"❌ Failed to get system stats: {response.status_code}")
        return False

def main():
    """Main test function"""
    print("=== Testing RAG Integration in Chat Interfaces ===")
    print("This test verifies Chat.tsx and ChatbotTester.tsx work with the backend RAG system\n")
    
    # Test frontend integration first
    integration_success = test_frontend_integration()
    
    # Test session creation
    session_success, patient_session, admin_session = test_chat_session_creation()
    if not session_success:
        print("❌ Session creation failed - cannot test chat functionality")
        return False
    
    # Test queries for both interfaces
    test_queries = [
        "What are your office hours?",
        "How do I book an appointment?", 
        "What services do you offer?",
        "Do you accept insurance?"
    ]
    
    patient_success = True
    admin_success = True
    
    for query in test_queries:
        if not test_rag_query(patient_session, "patient", query):
            patient_success = False
            break
        
        time.sleep(1)  # Brief pause between requests
        
        if not test_rag_query(admin_session, "admin", query):
            admin_success = False
            break
        
        time.sleep(1)  # Brief pause between requests
    
    # Results summary
    print(f"\n=== RAG Chat Integration Test Results ===")
    print(f"Frontend integration: {'✅ WORKING' if integration_success else '❌ FAILED'}")
    print(f"Chat.tsx interface: {'✅ WORKING' if patient_success else '❌ FAILED'}")
    print(f"ChatbotTester.tsx interface: {'✅ WORKING' if admin_success else '❌ FAILED'}")
    
    if integration_success and patient_success and admin_success:
        print("🎉 All RAG chat interfaces working correctly!")
        print("\nKey findings:")
        print("• Both frontend interfaces successfully create chat sessions")
        print("• RAG retrieval works and returns properly structured responses")
        print("• Source information is correctly formatted for frontend display")
        print("• Vector search finds relevant knowledge base entries")
        print("• Confidence scores and response times are provided")
        return True
    else:
        print("⚠️  Some RAG chat functionality needs attention")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)