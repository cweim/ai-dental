#!/usr/bin/env python3
"""
Initialize the dental knowledge base with embeddings and FAISS index.

This script will:
1. Check current knowledge base status
2. Load dental corpus if needed
3. Generate embeddings for all QA pairs
4. Build/rebuild FAISS index
5. Verify the system is ready
"""

import sys
import os
from sqlalchemy.orm import Session
import logging

# Add the current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db, SessionLocal
from models import KnowledgeBase
from embeddings_service import get_embeddings_service
from vector_search import get_vector_search_engine
from qa_management import get_qa_manager
from dental_corpus import get_dental_corpus_loader

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_knowledge_base_status(db: Session):
    """Check current status of knowledge base"""
    logger.info("=== Checking Knowledge Base Status ===")
    
    # Count total entries
    total_entries = db.query(KnowledgeBase).count()
    active_entries = db.query(KnowledgeBase).filter(KnowledgeBase.is_active == True).count()
    
    logger.info(f"Total KB entries: {total_entries}")
    logger.info(f"Active KB entries: {active_entries}")
    
    # Check embeddings status
    entries_with_embeddings = db.query(KnowledgeBase).filter(
        KnowledgeBase.embedding_vector.isnot(None),
        KnowledgeBase.is_active == True
    ).count()
    
    logger.info(f"Entries with embeddings: {entries_with_embeddings}")
    
    # Show sample entries
    if total_entries > 0:
        logger.info("\nSample entries:")
        sample_entries = db.query(KnowledgeBase).limit(3).all()
        for entry in sample_entries:
            logger.info(f"- ID {entry.id}: '{entry.question[:50]}...' (Category: {entry.category})")
    
    return {
        'total_entries': total_entries,
        'active_entries': active_entries,
        'entries_with_embeddings': entries_with_embeddings
    }

def load_dental_corpus(db: Session):
    """Load the dental corpus into knowledge base"""
    logger.info("=== Loading Dental Corpus ===")
    
    corpus_loader = get_dental_corpus_loader()
    qa_manager = get_qa_manager()
    
    dental_corpus = corpus_loader.get_dental_corpus()
    logger.info(f"Found {len(dental_corpus)} dental corpus entries")
    
    loaded_count = 0
    for qa_pair in dental_corpus:
        try:
            # Check if this question already exists
            existing = db.query(KnowledgeBase).filter(
                KnowledgeBase.question == qa_pair['question'],
                KnowledgeBase.source == 'dental_corpus'
            ).first()
            
            if existing:
                logger.debug(f"Skipping existing entry: '{qa_pair['question'][:30]}...'")
                continue
            
            # Create new entry
            kb_entry = qa_manager.create_qa_pair(
                db=db,
                question=qa_pair['question'],
                answer=qa_pair['answer'],
                category=qa_pair['category'],
                source=qa_pair['source']
            )
            
            if kb_entry:
                loaded_count += 1
                logger.info(f"Loaded: '{qa_pair['question'][:50]}...'")
            
        except Exception as e:
            logger.error(f"Error loading QA pair: {e}")
    
    logger.info(f"Successfully loaded {loaded_count} new dental corpus entries")
    return loaded_count

def rebuild_vector_index(db: Session):
    """Rebuild the FAISS vector index"""
    logger.info("=== Rebuilding Vector Index ===")
    
    embeddings_service = get_embeddings_service()
    vector_search = get_vector_search_engine()
    
    # Check embeddings service status
    logger.info(f"Embeddings service available: {embeddings_service.is_available}")
    logger.info(f"Embedding model: {embeddings_service.model_name}")
    logger.info(f"Embedding dimension: {embeddings_service.embedding_dimension}")
    
    # Rebuild embeddings for all entries
    rebuilt_count = embeddings_service.rebuild_embeddings(db)
    logger.info(f"Rebuilt embeddings for {rebuilt_count} entries")
    
    # Initialize/rebuild vector index
    success = vector_search.initialize_index(db)
    if success:
        logger.info("Vector index initialized successfully")
    else:
        logger.error("Failed to initialize vector index")
        return False
    
    # Check index status
    if vector_search.index:
        logger.info(f"FAISS index contains {vector_search.index.ntotal} vectors")
        logger.info(f"Index dimension: {vector_search.index.d}")
    
    return success

def test_search_functionality(db: Session):
    """Test the search functionality"""
    logger.info("=== Testing Search Functionality ===")
    
    vector_search = get_vector_search_engine()
    
    # Test queries
    test_queries = [
        "How often should I brush my teeth?",
        "What causes tooth decay?",
        "tooth pain relief",
        "dental checkup frequency"
    ]
    
    for query in test_queries:
        try:
            results = vector_search.search_with_details(query, k=3, threshold=0.5, db=db)
            logger.info(f"\nQuery: '{query}'")
            logger.info(f"Found {len(results)} results:")
            
            for i, result in enumerate(results[:2]):  # Show top 2
                logger.info(f"  {i+1}. Score: {result['similarity_score']:.3f}")
                logger.info(f"     Q: {result['question'][:60]}...")
                logger.info(f"     A: {result['answer'][:80]}...")
            
        except Exception as e:
            logger.error(f"Error testing query '{query}': {e}")

def main():
    """Main initialization function"""
    logger.info("=== AI Dentist Knowledge Base Initialization ===")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Step 1: Check current status
        status = check_knowledge_base_status(db)
        
        # Step 2: Load dental corpus if needed
        if status['total_entries'] < 10:  # Assume we need basic corpus
            load_dental_corpus(db)
            # Recheck status
            status = check_knowledge_base_status(db)
        
        # Step 3: Rebuild vector index
        if status['active_entries'] > 0:
            success = rebuild_vector_index(db)
            if not success:
                logger.error("Failed to rebuild vector index")
                return False
        else:
            logger.warning("No active entries found. Add some QA pairs first.")
            return False
        
        # Step 4: Test functionality
        test_search_functionality(db)
        
        logger.info("=== Initialization Complete ===")
        logger.info("The knowledge base is ready for use!")
        logger.info("You can now:")
        logger.info("1. Add QA pairs via the admin interface")
        logger.info("2. Test the chatbot functionality")
        logger.info("3. Use the vector search API")
        
        return True
        
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        return False
    
    finally:
        db.close()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)