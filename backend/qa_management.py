from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import logging
from datetime import datetime

from models import KnowledgeBase, ChatbotQA
from embeddings_service import get_embeddings_service
from vector_search import get_vector_search_engine

logger = logging.getLogger(__name__)

class QAManager:
    """Service for managing QA pairs and knowledge base entries"""
    
    def __init__(self):
        self.embeddings_service = get_embeddings_service()
        self.vector_search = get_vector_search_engine()
    
    def create_qa_pair(self, db: Session, question: str, answer: str, 
                      category: str = None, source: str = "user_defined",
                      source_url: str = None) -> Optional[KnowledgeBase]:
        """Create a new QA pair with embedding"""
        try:
            # Store in knowledge base with embedding
            kb_entry = self.embeddings_service.store_embedding(
                db=db,
                question=question,
                answer=answer,
                category=category,
                source=source,
                source_url=source_url
            )
            
            # Ensure vector search index is initialized before adding
            try:
                # Initialize index if not already done
                if not self.vector_search.index:
                    logger.info("Vector index not initialized. Initializing now...")
                    self.vector_search.initialize_index(db)
                
                # Add to vector search index
                self.vector_search.add_to_index(kb_entry)
                logger.info(f"Added KB entry {kb_entry.id} to vector index")
                
            except Exception as e:
                logger.warning(f"Could not add to vector index (will be included in next rebuild): {e}")
            
            # Also store in legacy chatbot_qa table for backward compatibility
            chatbot_qa = ChatbotQA(
                question=question,
                answer=answer,
                category=category
            )
            db.add(chatbot_qa)
            db.commit()
            
            logger.info(f"Created QA pair: {kb_entry.id}")
            return kb_entry
            
        except Exception as e:
            logger.error(f"Error creating QA pair: {e}")
            db.rollback()
            return None
    
    def update_qa_pair(self, db: Session, kb_id: int, question: str, answer: str,
                      category: str = None) -> bool:
        """Update an existing QA pair"""
        try:
            # Update knowledge base entry with new embedding
            success = self.embeddings_service.update_embedding(
                db=db,
                kb_id=kb_id,
                question=question,
                answer=answer
            )
            
            if success:
                # Update category if provided
                if category is not None:
                    kb_entry = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
                    if kb_entry:
                        kb_entry.category = category
                        db.commit()
                
                # Remove old entry from vector index and add updated entry
                kb_entry = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
                if kb_entry:
                    try:
                        # For now, rebuild index to ensure consistency
                        # TODO: Optimize to update single entry when FAISS supports it
                        logger.info(f"Rebuilding index to update KB entry {kb_id}")
                        self.vector_search.rebuild_index(db)
                    except Exception as e:
                        logger.warning(f"Could not update vector index: {e}")
                
                logger.info(f"Updated QA pair: {kb_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating QA pair: {e}")
            return False
    
    def delete_qa_pair(self, db: Session, kb_id: int) -> bool:
        """Delete a QA pair (soft delete)"""
        try:
            kb_entry = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
            if not kb_entry:
                return False
            
            # Soft delete
            kb_entry.is_active = False
            kb_entry.updated_at = datetime.utcnow()
            db.commit()
            
            # Remove from vector search index by rebuilding
            try:
                logger.info(f"Rebuilding index to remove KB entry {kb_id}")
                self.vector_search.rebuild_index(db)
            except Exception as e:
                logger.warning(f"Could not update vector index after deletion: {e}")
            
            logger.info(f"Deleted QA pair: {kb_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting QA pair: {e}")
            db.rollback()
            return False
    
    def get_qa_pair(self, db: Session, kb_id: int) -> Optional[KnowledgeBase]:
        """Get a single QA pair by ID"""
        try:
            return db.query(KnowledgeBase).filter(
                and_(KnowledgeBase.id == kb_id, KnowledgeBase.is_active == True)
            ).first()
            
        except Exception as e:
            logger.error(f"Error getting QA pair: {e}")
            return None
    
    def list_qa_pairs(self, db: Session, category: str = None, source: str = None,
                     limit: int = 100, offset: int = 0) -> List[KnowledgeBase]:
        """List QA pairs with optional filtering"""
        try:
            query = db.query(KnowledgeBase).filter(KnowledgeBase.is_active == True)
            
            if category:
                query = query.filter(KnowledgeBase.category == category)
            
            if source:
                query = query.filter(KnowledgeBase.source == source)
            
            return query.order_by(KnowledgeBase.created_at.desc()).offset(offset).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error listing QA pairs: {e}")
            return []
    
    def search_qa_pairs(self, db: Session, query: str, k: int = 5, 
                       threshold: float = 0.7, category: str = None) -> List[Dict]:
        """Search QA pairs using vector similarity"""
        try:
            # Use vector search
            results = self.vector_search.search_with_details(
                query=query,
                k=k,
                threshold=threshold,
                db=db
            )
            
            # Filter by category if specified
            if category:
                results = [r for r in results if r.get('category') == category]
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching QA pairs: {e}")
            return []
    
    def get_categories(self, db: Session) -> List[str]:
        """Get all available categories"""
        try:
            result = db.query(KnowledgeBase.category).filter(
                and_(KnowledgeBase.is_active == True, KnowledgeBase.category.isnot(None))
            ).distinct().all()
            
            return [r[0] for r in result if r[0]]
            
        except Exception as e:
            logger.error(f"Error getting categories: {e}")
            return []
    
    def get_sources(self, db: Session) -> List[str]:
        """Get all available sources"""
        try:
            result = db.query(KnowledgeBase.source).filter(
                and_(KnowledgeBase.is_active == True, KnowledgeBase.source.isnot(None))
            ).distinct().all()
            
            return [r[0] for r in result if r[0]]
            
        except Exception as e:
            logger.error(f"Error getting sources: {e}")
            return []
    
    def batch_create_qa_pairs(self, db: Session, qa_pairs: List[Dict]) -> List[KnowledgeBase]:
        """Create multiple QA pairs in batch"""
        try:
            # Use embeddings service batch functionality
            kb_entries = self.embeddings_service.batch_store_embeddings(db, qa_pairs)
            
            # Rebuild vector index to include new entries
            self.vector_search.rebuild_index(db)
            
            # Create legacy chatbot_qa entries for backward compatibility
            chatbot_qa_entries = []
            for pair in qa_pairs:
                chatbot_qa = ChatbotQA(
                    question=pair['question'],
                    answer=pair['answer'],
                    category=pair.get('category')
                )
                chatbot_qa_entries.append(chatbot_qa)
            
            db.add_all(chatbot_qa_entries)
            db.commit()
            
            logger.info(f"Batch created {len(kb_entries)} QA pairs")
            return kb_entries
            
        except Exception as e:
            logger.error(f"Error batch creating QA pairs: {e}")
            db.rollback()
            return []
    
    def duplicate_qa_pair(self, db: Session, kb_id: int, new_question: str = None) -> Optional[KnowledgeBase]:
        """Duplicate an existing QA pair"""
        try:
            original = self.get_qa_pair(db, kb_id)
            if not original:
                return None
            
            question = new_question or f"Copy of: {original.question}"
            
            return self.create_qa_pair(
                db=db,
                question=question,
                answer=original.answer,
                category=original.category,
                source=original.source,
                source_url=original.source_url
            )
            
        except Exception as e:
            logger.error(f"Error duplicating QA pair: {e}")
            return None
    
    def get_stats(self, db: Session) -> Dict:
        """Get QA management statistics"""
        try:
            total_active = db.query(KnowledgeBase).filter(KnowledgeBase.is_active == True).count()
            total_inactive = db.query(KnowledgeBase).filter(KnowledgeBase.is_active == False).count()
            
            # Count by source
            source_stats = {}
            sources = self.get_sources(db)
            for source in sources:
                count = db.query(KnowledgeBase).filter(
                    and_(KnowledgeBase.is_active == True, KnowledgeBase.source == source)
                ).count()
                source_stats[source] = count
            
            # Count by category
            category_stats = {}
            categories = self.get_categories(db)
            for category in categories:
                count = db.query(KnowledgeBase).filter(
                    and_(KnowledgeBase.is_active == True, KnowledgeBase.category == category)
                ).count()
                category_stats[category] = count
            
            return {
                'total_active': total_active,
                'total_inactive': total_inactive,
                'by_source': source_stats,
                'by_category': category_stats,
                'vector_index_stats': self.vector_search.get_stats()
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}
    
    def rebuild_embeddings(self, db: Session) -> bool:
        """Rebuild all embeddings and vector index"""
        try:
            # Rebuild embeddings
            count = self.embeddings_service.rebuild_embeddings(db)
            
            # Rebuild vector index
            success = self.vector_search.rebuild_index(db)
            
            if success:
                logger.info(f"Rebuilt embeddings and index for {count} entries")
            
            return success
            
        except Exception as e:
            logger.error(f"Error rebuilding embeddings: {e}")
            return False


# Global instance
_qa_manager = None

def get_qa_manager() -> QAManager:
    """Get global QA manager instance"""
    global _qa_manager
    if _qa_manager is None:
        _qa_manager = QAManager()
    return _qa_manager