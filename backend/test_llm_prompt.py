#!/usr/bin/env python3
"""
Test to show the exact LLM prompt construction and RAG context retrieval.
"""

import sys
import os
import requests
import json

API_BASE_URL = "http://localhost:8000"

def test_rag_context_retrieval():
    """Test how many QA pairs are retrieved and what context is used"""
    print("=== Testing RAG Context Retrieval ===")
    
    test_query = "What are your office hours?"
    
    # Test the search endpoint directly to see raw results
    print(f"🔍 Testing vector search for: '{test_query}'")
    search_response = requests.post(
        f"{API_BASE_URL}/api/chatbot/qa/search",
        headers={'Content-Type': 'application/json'},
        json={
            "query": test_query,
            "k": 5,  # This matches chatbot_service.py top_k = 5
            "threshold": 0.7  # This matches chatbot_service.py similarity_threshold = 0.7
        }
    )
    
    if search_response.status_code == 200:
        search_data = search_response.json()
        results = search_data.get('results', [])
        
        print(f"📊 Vector search found {len(results)} QA pairs")
        print(f"🎯 Similarity threshold: 0.7")
        print(f"📈 Top K results: 5")
        
        if results:
            print(f"\n📋 QA pairs that would be sent as context:")
            for i, result in enumerate(results, 1):
                score = result.get('similarity_score', 0)
                question = result.get('question', 'No question')
                answer = result.get('answer', 'No answer')
                category = result.get('category', 'No category')
                
                print(f"   {i}. [{category}] Score: {score:.3f}")
                print(f"      Q: {question}")
                print(f"      A: {answer[:100]}{'...' if len(answer) > 100 else ''}")
                print()
        
        # Show what the context would look like
        context_parts = []
        for result in results:
            context_parts.append(f"Q: {result['question']}\nA: {result['answer']}")
        
        context = "\n\n".join(context_parts)
        
        print(f"📝 Context that would be sent to LLM:")
        print("="*50)
        print(context)
        print("="*50)
        
        return results
    else:
        print(f"❌ Vector search failed: {search_response.status_code}")
        return []

def test_chat_flow():
    """Test the complete chat flow to see actual LLM prompt"""
    print(f"\n=== Testing Complete Chat Flow ===")
    
    # Create a chat session
    session_response = requests.post(
        f"{API_BASE_URL}/api/chatbot/chat/sessions",
        headers={'Content-Type': 'application/json'},
        json={"user_id": "test_prompt_user"}
    )
    
    if session_response.status_code != 200:
        print(f"❌ Failed to create chat session: {session_response.status_code}")
        return
    
    session = session_response.json()
    session_id = session['session_id']
    print(f"✅ Created chat session: {session_id[:8]}...")
    
    # Send a chat message
    test_query = "What are your office hours?"
    print(f"💬 Sending query: '{test_query}'")
    
    chat_response = requests.post(
        f"{API_BASE_URL}/api/chatbot/chat",
        headers={'Content-Type': 'application/json'},
        json={
            "query": test_query,
            "session_id": session_id,
            "user_id": "test_prompt_user"
        }
    )
    
    if chat_response.status_code == 200:
        chat_data = chat_response.json()
        
        print(f"🤖 LLM Response: {chat_data.get('response', 'No response')}")
        print(f"📊 Confidence Score: {chat_data.get('confidence_score', 0):.3f}")
        print(f"⏱️ Response Time: {chat_data.get('response_time_ms', 0)}ms")
        print(f"🔍 Search Results Used: {chat_data.get('search_results_count', 0)}")
        
        sources = chat_data.get('sources', [])
        if sources:
            print(f"\n📚 Sources used in response:")
            for i, source in enumerate(sources, 1):
                print(f"   {i}. KB#{source.get('kb_id')} - {source.get('question', 'No question')[:50]}...")
                print(f"      Category: {source.get('category')}, Score: {source.get('similarity_score', 0):.3f}")
        else:
            print(f"⚠️  No sources used in response")
    else:
        print(f"❌ Chat request failed: {chat_response.status_code}")

def show_prompt_structure():
    """Show the exact prompt structure used by the chatbot"""
    print(f"\n=== LLM Prompt Structure ===")
    
    print(f"🎯 SYSTEM PROMPT:")
    print("-" * 50)
    system_prompt = """You are a helpful dental assistant chatbot for an AI dentist practice. 

Your role is to:
1. Answer questions about dental health, procedures, and general dentistry
2. Provide helpful information based on the knowledge base context provided
3. Be friendly, professional, and supportive
4. Always recommend consulting with a dentist for personalized medical advice

Guidelines:
- Use the provided context to answer questions when relevant
- If you don't know something, admit it and suggest contacting the dental office
- Never provide specific medical diagnoses or treatment recommendations
- Keep responses concise but informative
- Always end with encouragement to schedule an appointment if needed

Remember: You are not a replacement for professional dental care, but a helpful assistant."""
    print(system_prompt)
    
    print(f"\n🎯 USER PROMPT TEMPLATE (with context):")
    print("-" * 50)
    user_prompt_template = """Based on the following dental knowledge base context, please answer the user's question:

CONTEXT:
{context}

USER QUESTION: {query}

Please provide a helpful response based on the context provided. If the context doesn't contain relevant information, provide general dental guidance and suggest contacting the dental office."""
    print(user_prompt_template)
    
    print(f"\n🎯 USER PROMPT TEMPLATE (without context):")
    print("-" * 50)
    fallback_template = """The user is asking: {query}

No specific context was found in the knowledge base. Please provide general dental guidance and suggest contacting the dental office for personalized advice."""
    print(fallback_template)

def main():
    """Main test function"""
    print("=== LLM Prompt Analysis for Chat Interfaces ===")
    print("Both ChatbotTester.tsx and Chat.tsx use the same backend endpoint")
    print("Analyzing how RAG context is retrieved and sent to LLM\n")
    
    # Show prompt structure
    show_prompt_structure()
    
    # Test RAG context retrieval
    search_results = test_rag_context_retrieval()
    
    # Test complete chat flow
    test_chat_flow()
    
    print(f"\n=== Analysis Summary ===")
    print(f"📝 LLM Model: llama3-8b-8192 (GROQ)")
    print(f"📊 Max QA pairs retrieved: 5 (top_k)")
    print(f"🎯 Similarity threshold: 0.7")
    print(f"📏 Max tokens per response: 500")
    print(f"🌡️ Temperature: 0.7")
    print(f"🔄 Context format: 'Q: question\\nA: answer' pairs separated by \\n\\n")
    print(f"✅ Both Chat.tsx and ChatbotTester.tsx use identical backend flow")
    
    if search_results:
        print(f"🎉 RAG system working correctly with {len(search_results)} context QA pairs!")
    else:
        print(f"⚠️  RAG system may need attention - no context retrieved")

if __name__ == "__main__":
    main()