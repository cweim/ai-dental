import os
import json
import pickle
import numpy as np
from typing import List, Dict, Optional, Tuple
import faiss
from sqlalchemy.orm import Session
import logging
from datetime import datetime

from models import KnowledgeBase, VectorSearchLog
from embeddings_service import get_embeddings_service
from exceptions import VectorSearchException, ExceptionHandler

logger = logging.getLogger(__name__)

class VectorSearchEngine:
    """FAISS-based vector search engine for semantic similarity search
    
    Automatically adapts to the embedding dimension from the embeddings service.
    Supports both SentenceTransformers (384-dim) and basic text similarity (128-dim).
    """
    
    def __init__(self):
        self.embeddings_service = get_embeddings_service()
        self.dimension = self.embeddings_service.embedding_dimension
        self.index = None
        self.id_mapping = {}  # Maps FAISS index positions to KnowledgeBase IDs
        self.index_path = "faiss_index.bin"
        self.mapping_path = "id_mapping.pkl"
        
        logger.info(f"VectorSearchEngine initialized with {self.dimension}-dimensional embeddings")
        
    def initialize_index(self, db: Session) -> bool:
        """Initialize FAISS index with existing knowledge base entries"""
        with ExceptionHandler("initialize_index"):
            try:
                # Check if we need to rebuild index due to dimension mismatch
                if os.path.exists(self.index_path) and os.path.exists(self.mapping_path):
                    try:
                        self.load_index()
                        # Verify dimension compatibility
                        if self.index.d != self.dimension:
                            logger.warning(f"Index dimension mismatch. Expected {self.dimension}, got {self.index.d}. Rebuilding index.")
                            return self.rebuild_index(db)
                        logger.info(f"Loaded existing FAISS index with {self.index.ntotal} vectors")
                        return True
                    except Exception as e:
                        logger.warning(f"Failed to load existing index: {e}. Creating new index.")
                
                # Create new index
                logger.info(f"Creating new FAISS index with dimension {self.dimension}")
                self.index = faiss.IndexFlatIP(self.dimension)  # Inner product (cosine similarity)
                self.id_mapping = {}
                
                # Load all active knowledge base entries
                kb_entries = db.query(KnowledgeBase).filter(KnowledgeBase.is_active == True).all()
                
                if not kb_entries:
                    logger.warning("No knowledge base entries found for indexing")
                    self.save_index()  # Save empty index
                    return True
                
                # Prepare embeddings
                embeddings = []
                valid_entries = []
                
                for i, entry in enumerate(kb_entries):
                    embedding = self.embeddings_service.get_embedding_from_db(entry)
                    if embedding and len(embedding) == self.dimension:
                        embeddings.append(embedding)
                        valid_entries.append(entry)
                        self.id_mapping[len(embeddings) - 1] = entry.id
                    else:
                        if not embedding:
                            logger.warning(f"No embedding found for KB entry {entry.id}")
                        else:
                            logger.warning(f"Dimension mismatch for KB entry {entry.id}. Expected {self.dimension}, got {len(embedding)}")
                
                if embeddings:
                    # Convert to numpy array and normalize for cosine similarity
                    embeddings_array = np.array(embeddings, dtype=np.float32)
                    faiss.normalize_L2(embeddings_array)
                    
                    # Add to index
                    self.index.add(embeddings_array)
                    
                    # Save index
                    self.save_index()
                    
                    logger.info(f"Initialized FAISS index with {len(embeddings)} entries")
                else:
                    logger.warning("No valid embeddings found for indexing")
                
                return True
                
            except Exception as e:
                logger.error(f"Error initializing index: {e}")
                raise VectorSearchException(f"Failed to initialize vector search index: {str(e)}")
    
    def add_to_index(self, kb_entry: KnowledgeBase) -> bool:
        """Add a single knowledge base entry to the index"""
        with ExceptionHandler("add_to_index"):
            try:
                if not self.index:
                    raise VectorSearchException("Index not initialized")
                
                # Get embedding
                embedding = self.embeddings_service.get_embedding_from_db(kb_entry)
                if not embedding:
                    raise VectorSearchException(f"No embedding found for KB entry {kb_entry.id}")
                
                # Validate dimension
                if len(embedding) != self.dimension:
                    raise VectorSearchException(
                        f"Dimension mismatch for KB entry {kb_entry.id}. Expected {self.dimension}, got {len(embedding)}"
                    )
                
                # Normalize embedding
                embedding_array = np.array([embedding], dtype=np.float32)
                faiss.normalize_L2(embedding_array)
                
                # Add to index
                current_size = self.index.ntotal
                self.index.add(embedding_array)
                
                # Update mapping
                self.id_mapping[current_size] = kb_entry.id
                
                # Save updated index
                self.save_index()
                
                logger.info(f"Added KB entry {kb_entry.id} to index at position {current_size}")
                return True
                
            except VectorSearchException:
                raise
            except Exception as e:
                raise VectorSearchException(f"Failed to add entry to index: {str(e)}")
    
    def remove_from_index(self, kb_id: int) -> bool:
        """Remove a knowledge base entry from the index"""
        try:
            # Find the index position
            index_position = None
            for pos, mapped_id in self.id_mapping.items():
                if mapped_id == kb_id:
                    index_position = pos
                    break
            
            if index_position is None:
                logger.warning(f"KB entry {kb_id} not found in index")
                return False
            
            # FAISS doesn't support direct removal, so we need to rebuild
            logger.info(f"Rebuilding index to remove KB entry {kb_id}")
            # This is a placeholder - in production, you might want to implement
            # a more efficient removal strategy or use a different index type
            
            return True
            
        except Exception as e:
            logger.error(f"Error removing from index: {e}")
            return False
    
    def search(self, query: str, k: int = 5, threshold: float = 0.7, 
               session_id: str = None, db: Session = None) -> List[Dict]:
        """Search for similar knowledge base entries using vector similarity"""
        with ExceptionHandler("vector_search"):
            try:
                if not self.index:
                    logger.warning("Vector search index not initialized. Attempting auto-initialization...")
                    if db:
                        success = self.initialize_index(db)
                        if not success:
                            raise VectorSearchException("Vector search index not initialized and auto-initialization failed")
                    else:
                        raise VectorSearchException("Vector search index not initialized and no database session provided for auto-initialization")
                
                if not query.strip():
                    raise VectorSearchException("Query cannot be empty")
                
                start_time = datetime.utcnow()
                
                # Generate query embedding
                query_embedding = self.embeddings_service.generate_embedding(query)
                
                # Validate embedding dimension
                if len(query_embedding) != self.dimension:
                    raise VectorSearchException(
                        f"Query embedding dimension mismatch. Expected {self.dimension}, got {len(query_embedding)}"
                    )
                
                # Normalize embedding for cosine similarity
                query_array = np.array([query_embedding], dtype=np.float32)
                faiss.normalize_L2(query_array)
                
                # Perform vector search
                scores, indices = self.index.search(query_array, min(k, self.index.ntotal))
                
                # Process results
                results = []
                for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                    if idx == -1:  # FAISS returns -1 for invalid indices
                        continue
                    
                    if score < threshold:
                        logger.debug(f"Filtering result with score {score} below threshold {threshold}")
                        continue
                    
                    kb_id = self.id_mapping.get(idx)
                    if kb_id:
                        results.append({
                            'kb_id': kb_id,
                            'similarity_score': float(score),
                            'rank': i + 1,
                            'index_position': int(idx)
                        })
                
                # Log search if database session provided
                if db and session_id:
                    search_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                    self._log_search(db, session_id, query, k, results, search_time_ms)
                
                logger.info(f"Vector search completed: {len(results)} results for query '{query[:50]}...'")
                return results
                
            except VectorSearchException:
                raise
            except Exception as e:
                raise VectorSearchException(f"Vector search failed: {str(e)}")
    
    def search_with_details(self, query: str, k: int = 5, threshold: float = 0.7,
                           session_id: str = None, db: Session = None) -> List[Dict]:
        """Search with full knowledge base entry details"""
        try:
            # Get basic search results
            search_results = self.search(query, k, threshold, session_id, db)
            
            if not search_results or not db:
                return search_results
            
            # Fetch full KB entries
            kb_ids = [result['kb_id'] for result in search_results]
            kb_entries = db.query(KnowledgeBase).filter(KnowledgeBase.id.in_(kb_ids)).all()
            
            # Create lookup
            kb_lookup = {entry.id: entry for entry in kb_entries}
            
            # Enhance results with full details
            detailed_results = []
            for result in search_results:
                kb_entry = kb_lookup.get(result['kb_id'])
                if kb_entry:
                    detailed_results.append({
                        'kb_id': result['kb_id'],
                        'question': kb_entry.question,
                        'answer': kb_entry.answer,
                        'category': kb_entry.category,
                        'source': kb_entry.source,
                        'source_url': kb_entry.source_url,
                        'similarity_score': result['similarity_score'],
                        'rank': result['rank']
                    })
            
            return detailed_results
            
        except Exception as e:
            logger.error(f"Error during detailed search: {e}")
            return []
    
    def _log_search(self, db: Session, session_id: str, query: str, k: int, 
                   results: List[Dict], search_time_ms: int):
        """Log search query and results"""
        try:
            similarity_scores = [result['similarity_score'] for result in results]
            kb_ids = [result['kb_id'] for result in results]
            
            search_log = VectorSearchLog(
                session_id=session_id,
                query=query,
                top_k=k,
                similarity_scores=json.dumps(similarity_scores),
                matched_kb_ids=json.dumps(kb_ids),
                search_time_ms=search_time_ms
            )
            
            db.add(search_log)
            db.commit()
            
        except Exception as e:
            logger.error(f"Error logging search: {e}")
    
    def rebuild_index(self, db: Session) -> bool:
        """Rebuild the entire FAISS index from scratch"""
        try:
            logger.info("Rebuilding FAISS index from scratch")
            
            # Clear existing index and mapping
            self.index = faiss.IndexFlatIP(self.dimension)
            self.id_mapping = {}
            
            # Load all active knowledge base entries
            kb_entries = db.query(KnowledgeBase).filter(KnowledgeBase.is_active == True).all()
            
            if not kb_entries:
                logger.warning("No active knowledge base entries found")
                self.save_index()  # Save empty index
                return True
            
            # Prepare embeddings
            embeddings = []
            valid_entries = []
            
            for i, entry in enumerate(kb_entries):
                embedding = self.embeddings_service.get_embedding_from_db(entry)
                if embedding and len(embedding) == self.dimension:
                    embeddings.append(embedding)
                    valid_entries.append(entry)
                    self.id_mapping[len(embeddings) - 1] = entry.id
                else:
                    if not embedding:
                        logger.warning(f"No embedding found for KB entry {entry.id}")
                    else:
                        logger.warning(f"Dimension mismatch for KB entry {entry.id}. Expected {self.dimension}, got {len(embedding)}")
            
            if embeddings:
                # Convert to numpy array and normalize for cosine similarity
                embeddings_array = np.array(embeddings, dtype=np.float32)
                faiss.normalize_L2(embeddings_array)
                
                # Add to index
                self.index.add(embeddings_array)
                
                # Save index
                self.save_index()
                
                logger.info(f"Rebuilt FAISS index with {len(embeddings)} entries")
            else:
                logger.warning("No valid embeddings found for indexing")
                self.save_index()  # Save empty index
            
            return True
            
        except Exception as e:
            logger.error(f"Error rebuilding index: {e}")
            return False
    
    def save_index(self):
        """Save FAISS index and ID mapping to disk"""
        try:
            if self.index:
                faiss.write_index(self.index, self.index_path)
                
                with open(self.mapping_path, 'wb') as f:
                    pickle.dump(self.id_mapping, f)
                
                logger.debug("FAISS index saved to disk")
            
        except Exception as e:
            logger.error(f"Error saving index: {e}")
    
    def load_index(self):
        """Load FAISS index and ID mapping from disk"""
        try:
            if os.path.exists(self.index_path) and os.path.exists(self.mapping_path):
                self.index = faiss.read_index(self.index_path)
                
                with open(self.mapping_path, 'rb') as f:
                    self.id_mapping = pickle.load(f)
                
                logger.info(f"FAISS index loaded with {self.index.ntotal} entries")
            
        except Exception as e:
            logger.error(f"Error loading index: {e}")
    
    def get_stats(self) -> Dict:
        """Get index statistics"""
        try:
            if not self.index:
                return {'status': 'not_initialized'}
            
            return {
                'status': 'ready',
                'total_entries': self.index.ntotal,
                'dimension': self.dimension,
                'index_type': 'IndexFlatIP'
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {'status': 'error', 'error': str(e)}


# Global instance
_vector_search_engine = None

def get_vector_search_engine() -> VectorSearchEngine:
    """Get global vector search engine instance"""
    global _vector_search_engine
    if _vector_search_engine is None:
        _vector_search_engine = VectorSearchEngine()
    return _vector_search_engine