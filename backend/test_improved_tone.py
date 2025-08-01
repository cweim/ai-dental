#!/usr/bin/env python3
"""
Test improved conversational tone in LLM responses.
"""

import sys
import os
import requests
import json

API_BASE_URL = "http://localhost:8000"

def test_conversational_tone():
    """Test that responses use natural, conversational tone"""
    print("=== Testing Improved Conversational Tone ===")
    
    # Create session
    session_response = requests.post(
        f"{API_BASE_URL}/api/chatbot/chat/sessions",
        headers={'Content-Type': 'application/json'},
        json={"user_id": "test_improved_tone"}
    )
    
    if session_response.status_code != 200:
        print(f"❌ Failed to create session: {session_response.status_code}")
        return False
    
    session_id = session_response.json()['session_id']
    print(f"✅ Created session: {session_id[:8]}...")
    
    test_cases = [
        {
            "query": "Where is your clinic located",
            "expected_phrases": ["Based on what I know", "our dental clinic", "112 Lengkong Tiga"],
            "avoid_phrases": ["Thank you for reaching out", "According to our context", "According to the context"]
        },
        {
            "query": "What are your office hours",
            "expected_phrases": ["Monday through Friday", "8:00 AM to 6:00 PM", "Saturday"],
            "avoid_phrases": ["Thank you for reaching out", "According to our context", "According to the context"]
        },
        {
            "query": "How often should I brush my teeth",
            "expected_phrases": ["twice a day", "fluoride toothpaste", "2 minutes"],
            "avoid_phrases": ["Thank you for reaching out", "According to our context", "No specific context"]
        }
    ]
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 Test {i}: '{test_case['query']}'")
        
        response = requests.post(
            f"{API_BASE_URL}/api/chatbot/chat",
            headers={'Content-Type': 'application/json'},
            json={
                "query": test_case['query'],
                "session_id": session_id,
                "user_id": "test_improved_tone"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            response_text = data.get('response', '').lower()
            
            # Check for expected phrases
            found_expected = []
            for phrase in test_case['expected_phrases']:
                if phrase.lower() in response_text:
                    found_expected.append(phrase)
            
            # Check for avoided phrases
            found_avoided = []
            for phrase in test_case['avoid_phrases']:
                if phrase.lower() in response_text:
                    found_avoided.append(phrase)
            
            # Evaluate tone
            conversational_indicators = [
                "hi there", "so you're", "based on what i know", 
                "from our clinic", "it's always", "i recommend",
                "feel free", "happy to help"
            ]
            
            tone_score = sum(1 for indicator in conversational_indicators if indicator in response_text)
            
            print(f"   📝 Response length: {len(data.get('response', ''))} characters")
            print(f"   ✅ Found expected phrases: {len(found_expected)}/{len(test_case['expected_phrases'])}")
            print(f"   🚫 Avoided formal phrases: {len(found_avoided) == 0}")
            print(f"   💬 Conversational tone score: {tone_score}")
            
            if found_expected and not found_avoided and tone_score > 0:
                print(f"   ✅ PASSED - Natural, conversational tone")
            else:
                print(f"   ❌ FAILED - Tone needs improvement")
                all_passed = False
                if found_avoided:
                    print(f"      Found unwanted phrases: {found_avoided}")
        else:
            print(f"   ❌ Request failed: {response.status_code}")
            all_passed = False
    
    return all_passed

def analyze_tone_improvements():
    """Analyze the specific improvements made"""
    print(f"\n=== Tone Improvement Analysis ===")
    
    print(f"🎯 BEFORE (Formal/Robotic):")
    print(f"   ❌ 'Thank you for reaching out to our dental practice!'")
    print(f"   ❌ 'According to our context, our clinic is located...'")
    print(f"   ❌ 'Based on the following dental knowledge base context...'")
    print(f"   ❌ Overly formal and repetitive introductions")
    
    print(f"\n🎉 AFTER (Natural/Conversational):")
    print(f"   ✅ 'Hi there! Based on what I know...'")
    print(f"   ✅ 'So you're wondering about...'")
    print(f"   ✅ 'From our clinic information...'")
    print(f"   ✅ Natural, friendly, and helpful tone")
    
    print(f"\n📋 KEY CHANGES:")
    print(f"   1. 🗣️ More conversational language")
    print(f"   2. 🚫 Removed formal corporate phrases")
    print(f"   3. 💬 Natural context integration")
    print(f"   4. 😊 Friendly, approachable tone")
    print(f"   5. 🎯 Direct and helpful responses")

def test_clinic_vs_general_info():
    """Test that both clinic-specific and general dental info are handled well"""
    print(f"\n=== Testing Clinic vs General Information ===")
    
    session_response = requests.post(
        f"{API_BASE_URL}/api/chatbot/chat/sessions",
        headers={'Content-Type': 'application/json'},
        json={"user_id": "test_info_types"}
    )
    
    session_id = session_response.json()['session_id']
    
    test_cases = [
        {
            "query": "Where is your clinic located",
            "type": "clinic_specific",
            "should_have_sources": True
        },
        {
            "query": "How to prevent tooth decay",
            "type": "general_dental",
            "should_have_sources": False  # May or may not have sources
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🔍 Testing {test_case['type']}: '{test_case['query']}'")
        
        response = requests.post(
            f"{API_BASE_URL}/api/chatbot/chat",
            headers={'Content-Type': 'application/json'},
            json={
                "query": test_case['query'],
                "session_id": session_id,
                "user_id": "test_info_types"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            sources = data.get('sources', [])
            response_text = data.get('response', '')
            
            print(f"   📊 Sources found: {len(sources)}")
            print(f"   📝 Response quality: {'Good' if len(response_text) > 100 else 'Short'}")
            
            if test_case['type'] == 'clinic_specific':
                if sources:
                    print(f"   ✅ Clinic-specific info with sources")
                else:
                    print(f"   ⚠️  Clinic query but no sources found")
            else:
                print(f"   ✅ General dental information provided")

def main():
    """Main test function"""
    print("=== Testing Improved LLM Response Tone ===")
    print("Goal: Natural, conversational responses for dental assistance\n")
    
    tone_success = test_conversational_tone()
    analyze_tone_improvements()
    test_clinic_vs_general_info()
    
    print(f"\n=== Tone Improvement Test Results ===")
    print(f"Conversational tone: {'✅ IMPROVED' if tone_success else '❌ NEEDS WORK'}")
    
    if tone_success:
        print("🎉 LLM responses now use natural, conversational tone!")
        print("\nKey improvements:")
        print("• Removed formal corporate language")
        print("• Uses 'Based on what I know' instead of 'According to context'")
        print("• More friendly and approachable responses")
        print("• Natural integration of clinic and general dental information")
        return True
    else:
        print("⚠️  Response tone may need further refinement")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)