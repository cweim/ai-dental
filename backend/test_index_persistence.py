#!/usr/bin/env python3
"""
Test vector index persistence and identify potential causes for rebuilding needs.
"""

import sys
import os
import requests
import json
import time
from datetime import datetime

API_BASE_URL = "http://localhost:8000"

def check_index_files():
    """Check if index files exist and their details"""
    print("=== Checking Index File Persistence ===")
    
    index_file = "/Users/chinweiming/Desktop/Projects/AI-dentist/backend/faiss_index.bin"
    mapping_file = "/Users/chinweiming/Desktop/Projects/AI-dentist/backend/id_mapping.pkl"
    
    files_info = {}
    
    for file_path, name in [(index_file, "FAISS Index"), (mapping_file, "ID Mapping")]:
        if os.path.exists(file_path):
            stat = os.stat(file_path)
            files_info[name] = {
                'exists': True,
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'path': file_path
            }
            print(f"✅ {name}: {stat.st_size} bytes, modified {files_info[name]['modified']}")
        else:
            files_info[name] = {'exists': False}
            print(f"❌ {name}: File not found")
    
    return files_info

def test_index_status():
    """Test current vector index status"""
    print(f"\n=== Testing Vector Index Status ===")
    
    response = requests.get(f"{API_BASE_URL}/api/chatbot/system/stats")
    if response.status_code == 200:
        stats = response.json()
        vector_stats = stats.get('vector_search', {})
        
        print(f"📊 Status: {vector_stats.get('status', 'unknown')}")
        print(f"📈 Entries: {vector_stats.get('total_entries', 'unknown')}")
        print(f"🔢 Dimension: {vector_stats.get('dimension', 'unknown')}")
        print(f"🏗️ Index Type: {vector_stats.get('index_type', 'unknown')}")
        
        return vector_stats.get('status') == 'ready'
    else:
        print(f"❌ Failed to get system stats: {response.status_code}")
        return False

def test_search_consistency():
    """Test if search results are consistent"""
    print(f"\n=== Testing Search Consistency ===")
    
    test_queries = [
        "Where is your clinic located",
        "What are your office hours", 
        "Do you accept insurance"
    ]
    
    consistent = True
    
    for query in test_queries:
        print(f"\n🔍 Testing: '{query}'")
        
        # Test multiple times to check consistency
        results_list = []
        for i in range(3):
            response = requests.post(
                f"{API_BASE_URL}/api/chatbot/qa/search",
                headers={'Content-Type': 'application/json'},
                json={
                    "query": query,
                    "k": 3,
                    "threshold": 0.5
                }
            )
            
            if response.status_code == 200:
                results = response.json().get('results', [])
                results_list.append(len(results))
                time.sleep(0.1)  # Small delay
            else:
                print(f"   ❌ Search {i+1} failed: {response.status_code}")
                consistent = False
        
        if len(set(results_list)) == 1:
            print(f"   ✅ Consistent results: {results_list[0]} entries each time")
        else:
            print(f"   ❌ Inconsistent results: {results_list}")
            consistent = False
    
    return consistent

def identify_potential_causes():
    """Identify potential causes for index rebuilding needs"""
    print(f"\n=== Potential Causes for Index Rebuilding ===")
    
    causes = []
    
    # Check 1: Server restarts
    print(f"1. 🔄 Server Restart Issues:")
    print(f"   - FAISS index is stored in memory AND persisted to disk")
    print(f"   - If server restarts, index should auto-load from disk")
    print(f"   - Check: Are index files being deleted or corrupted?")
    
    # Check 2: Dimension mismatches
    print(f"\n2. 📏 Embedding Dimension Changes:")
    print(f"   - Current embeddings service uses 384-dimensional vectors")
    print(f"   - If embeddings service changes, index becomes incompatible")
    print(f"   - Check: Consistent embedding model (all-MiniLM-L6-v2)?")
    
    # Check 3: File permissions
    print(f"\n3. 🔒 File Permissions:")
    index_files = [
        "/Users/chinweiming/Desktop/Projects/AI-dentist/backend/faiss_index.bin",
        "/Users/chinweiming/Desktop/Projects/AI-dentist/backend/id_mapping.pkl"
    ]
    
    for file_path in index_files:
        if os.path.exists(file_path):
            stat = os.stat(file_path)
            permissions = oct(stat.st_mode)[-3:]
            print(f"   - {os.path.basename(file_path)}: {permissions} permissions")
        else:
            print(f"   - {os.path.basename(file_path)}: File missing!")
            causes.append("Missing index files")
    
    # Check 4: QA pair modifications
    print(f"\n4. 📝 QA Pair Modifications:")
    print(f"   - Adding new QA pairs should auto-update index")
    print(f"   - Editing QA pairs should rebuild index")
    print(f"   - Deleting QA pairs should rebuild index")
    print(f"   - Check: Are these operations calling rebuild correctly?")
    
    # Check 5: Memory issues
    print(f"\n5. 💾 Memory Issues:")
    print(f"   - FAISS index stored in memory for fast access")
    print(f"   - Large indexes might cause memory pressure")
    print(f"   - Check: Server memory usage and potential OOM kills")
    
    return causes

def test_qa_operations_trigger_rebuild():
    """Test if QA operations properly maintain index"""
    print(f"\n=== Testing QA Operations Index Maintenance ===")
    
    # Get initial stats
    initial_response = requests.get(f"{API_BASE_URL}/api/chatbot/system/stats")
    if initial_response.status_code != 200:
        print(f"❌ Cannot get initial stats")
        return False
    
    initial_entries = initial_response.json().get('vector_search', {}).get('total_entries', 0)
    print(f"📊 Initial index entries: {initial_entries}")
    
    # Create a test QA pair
    test_qa = {
        "question": "Test question for index persistence",
        "answer": "Test answer for checking if index updates automatically",
        "category": "test",
        "source": "index_test"
    }
    
    create_response = requests.post(
        f"{API_BASE_URL}/api/chatbot/qa",
        headers={'Content-Type': 'application/json'},
        json=test_qa
    )
    
    if create_response.status_code != 200:
        print(f"❌ Failed to create test QA: {create_response.status_code}")
        return False
    
    created_qa = create_response.json()
    test_id = created_qa['id']
    print(f"✅ Created test QA pair: ID {test_id}")
    
    # Check if index was updated
    time.sleep(1)  # Wait for potential async updates
    
    updated_response = requests.get(f"{API_BASE_URL}/api/chatbot/system/stats")
    if updated_response.status_code == 200:
        updated_entries = updated_response.json().get('vector_search', {}).get('total_entries', 0)
        print(f"📊 Updated index entries: {updated_entries}")
        
        if updated_entries > initial_entries:
            print(f"✅ Index automatically updated (+{updated_entries - initial_entries} entries)")
        else:
            print(f"⚠️  Index may not have auto-updated")
    
    # Clean up test QA pair
    delete_response = requests.delete(f"{API_BASE_URL}/api/chatbot/qa/{test_id}")
    if delete_response.status_code == 200:
        print(f"✅ Cleaned up test QA pair")
    
    return True

def main():
    """Main diagnostic function"""
    print("=== Vector Index Persistence Diagnostic ===")
    print("Investigating why index might need frequent rebuilding\n")
    
    # Run diagnostic tests
    file_info = check_index_files()
    index_ready = test_index_status()
    search_consistent = test_search_consistency()
    identify_potential_causes()
    qa_ops_working = test_qa_operations_trigger_rebuild()
    
    print(f"\n=== Diagnostic Summary ===")
    print(f"Index files present: {'✅' if all(info.get('exists', False) for info in file_info.values()) else '❌'}")
    print(f"Index status ready: {'✅' if index_ready else '❌'}")
    print(f"Search consistency: {'✅' if search_consistent else '❌'}")
    print(f"QA operations: {'✅' if qa_ops_working else '❌'}")
    
    print(f"\n💡 Recommendations:")
    print(f"1. Monitor server logs for index loading errors")
    print(f"2. Check if server restarts are causing index loss")
    print(f"3. Verify file permissions allow reading/writing index files")
    print(f"4. Ensure QA operations properly trigger index updates")
    print(f"5. Consider implementing index health checks on startup")
    
    if index_ready and search_consistent:
        print(f"\n✅ Index appears healthy - rebuilding needs may be intermittent")
    else:
        print(f"\n⚠️  Index issues detected - investigate further")

if __name__ == "__main__":
    main()