#!/usr/bin/env python3
"""
Test QA pair edit and delete operations to verify vector database updates.
"""

import sys
import os
import requests
import json

# Add the current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

API_BASE_URL = "http://localhost:8000"

def test_edit_qa_pair():
    """Test editing a QA pair"""
    print("=== Testing QA Pair Edit ===")
    
    # Get a QA pair to edit
    response = requests.get(f"{API_BASE_URL}/api/chatbot/qa?limit=1")
    if response.status_code != 200:
        print(f"Failed to get QA pairs: {response.status_code}")
        return False
    
    qa_pairs = response.json()
    if not qa_pairs:
        print("No QA pairs found")
        return False
    
    qa_pair = qa_pairs[0]
    qa_id = qa_pair['id']
    original_answer = qa_pair['answer']
    
    print(f"Original QA {qa_id}: {qa_pair['question'][:50]}...")
    print(f"Original answer: {original_answer[:50]}...")
    
    # Update the QA pair
    updated_data = {
        "question": qa_pair['question'],
        "answer": original_answer + " [UPDATED FOR TESTING]",
        "category": qa_pair['category']
    }
    
    response = requests.put(
        f"{API_BASE_URL}/api/chatbot/qa/{qa_id}",
        json=updated_data
    )
    
    if response.status_code == 200:
        print("✅ QA pair updated successfully")
        
        # Verify the update
        response = requests.get(f"{API_BASE_URL}/api/chatbot/qa/{qa_id}")
        if response.status_code == 200:
            updated_qa = response.json()
            if "[UPDATED FOR TESTING]" in updated_qa['answer']:
                print("✅ Update verified in database")
                
                # Test vector search to see if updated
                search_response = requests.post(
                    f"{API_BASE_URL}/api/chatbot/qa/search",
                    json={
                        "query": qa_pair['question'][:20],
                        "k": 3,
                        "threshold": 0.3
                    }
                )
                
                if search_response.status_code == 200:
                    search_results = search_response.json()['results']
                    found_updated = False
                    for result in search_results:
                        if result['kb_id'] == qa_id and "[UPDATED FOR TESTING]" in result['answer']:
                            found_updated = True
                            break
                    
                    if found_updated:
                        print("✅ Updated entry found in vector search")
                        return True
                    else:
                        print("❌ Updated entry not found in vector search")
                        return False
                else:
                    print(f"❌ Vector search failed: {search_response.status_code}")
                    return False
            else:
                print("❌ Update not reflected in database")
                return False
        else:
            print(f"❌ Failed to verify update: {response.status_code}")
            return False
    else:
        print(f"❌ Failed to update QA pair: {response.status_code} - {response.text}")
        return False

def test_delete_qa_pair():
    """Test deleting a QA pair"""
    print("\n=== Testing QA Pair Delete ===")
    
    # Create a test QA pair first
    test_data = {
        "question": "This is a test question for deletion",
        "answer": "This is a test answer that will be deleted",
        "category": "test",
        "source": "test_deletion"
    }
    
    # Create the QA pair
    response = requests.post(f"{API_BASE_URL}/api/chatbot/qa", json=test_data)
    if response.status_code != 200:
        print(f"❌ Failed to create test QA pair: {response.status_code}")
        return False
    
    created_qa = response.json()
    qa_id = created_qa['id']
    print(f"Created test QA pair with ID: {qa_id}")
    
    # Verify it's searchable
    search_response = requests.post(
        f"{API_BASE_URL}/api/chatbot/qa/search",
        json={
            "query": "test question deletion",
            "k": 5,
            "threshold": 0.3
        }
    )
    
    before_delete_found = False
    if search_response.status_code == 200:
        results = search_response.json()['results']
        for result in results:
            if result['kb_id'] == qa_id:
                before_delete_found = True
                print("✅ Test QA pair found in vector search before deletion")
                break
    
    if not before_delete_found:
        print("⚠️  Test QA pair not found in vector search before deletion")
    
    # Delete the QA pair
    response = requests.delete(f"{API_BASE_URL}/api/chatbot/qa/{qa_id}")
    if response.status_code == 200:
        print("✅ QA pair deleted successfully")
        
        # Verify it's no longer in the main list (should be inactive)
        response = requests.get(f"{API_BASE_URL}/api/chatbot/qa")
        if response.status_code == 200:
            all_qa_pairs = response.json()
            found_active = False
            for qa in all_qa_pairs:
                if qa['id'] == qa_id and qa['is_active']:
                    found_active = True
                    break
            
            if not found_active:
                print("✅ Deleted QA pair not found in active entries")
                
                # Test vector search to ensure it's removed
                search_response = requests.post(
                    f"{API_BASE_URL}/api/chatbot/qa/search",
                    json={
                        "query": "test question deletion",
                        "k": 5,
                        "threshold": 0.3
                    }
                )
                
                after_delete_found = False
                if search_response.status_code == 200:
                    results = search_response.json()['results']
                    for result in results:
                        if result['kb_id'] == qa_id:
                            after_delete_found = True
                            break
                
                if not after_delete_found:
                    print("✅ Deleted QA pair not found in vector search")
                    return True
                else:
                    print("❌ Deleted QA pair still found in vector search")
                    return False
            else:
                print("❌ Deleted QA pair still active in database")
                return False
        else:
            print(f"❌ Failed to verify deletion: {response.status_code}")
            return False
    else:
        print(f"❌ Failed to delete QA pair: {response.status_code} - {response.text}")
        return False

def main():
    """Main test function"""
    print("=== Testing QA Pair Operations ===")
    
    edit_success = test_edit_qa_pair()
    delete_success = test_delete_qa_pair()
    
    print(f"\n=== Results ===")
    print(f"Edit functionality: {'✅ WORKING' if edit_success else '❌ FAILED'}")
    print(f"Delete functionality: {'✅ WORKING' if delete_success else '❌ FAILED'}")
    
    if edit_success and delete_success:
        print("🎉 All QA operations working correctly with vector database updates!")
        return True
    else:
        print("⚠️  Some QA operations need fixing")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)