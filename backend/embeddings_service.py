import os
import json
import numpy as np
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
import logging
from datetime import datetime

from models import KnowledgeBase
from database import get_db

logger = logging.getLogger(__name__)

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("sentence-transformers not installed. Install with: pip install sentence-transformers")

class EmbeddingsService:
    """Service for generating and managing embeddings for vector search using Sentence Transformers
    
    Uses all-MiniLM-L6-v2 model for generating high-quality 384-dimensional embeddings
    optimized for semantic similarity tasks including medical/dental text.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.embedding_dimension = 384  # all-MiniLM-L6-v2 produces 384-dim embeddings
        self.max_tokens = 512  # Model's max sequence length
        
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                logger.info(f"Loading SentenceTransformer model: {model_name}")
                self.model = SentenceTransformer(model_name)
                self.is_available = True
                logger.info("Embeddings service initialized successfully")
            except Exception as e:
                logger.error(f"Failed to load SentenceTransformer model: {e}")
                self.is_available = False
                self._fallback_to_basic()
        else:
            self.is_available = False
            self._fallback_to_basic()
    
    def _fallback_to_basic(self):
        """Fallback to basic text similarity if SentenceTransformers is not available"""
        logger.warning("Falling back to basic text similarity approach")
        self.model_name = "basic-text-similarity"
        self.embedding_dimension = 128
        self.is_available = False
        
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text using SentenceTransformers or fallback to basic approach"""
        try:
            # Clean text
            cleaned_text = self._clean_text(text)
            
            if self.is_available:
                # Use SentenceTransformers for proper embeddings
                embedding = self.model.encode(cleaned_text, convert_to_tensor=False)
                return embedding.tolist()
            else:
                # Fallback to basic approach
                return self._generate_basic_embedding(cleaned_text)
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    def _generate_basic_embedding(self, text: str) -> List[float]:
        """Generate a basic embedding using simple text features"""
        # This is a simplified approach - in production, use proper embeddings
        
        # Character frequency features
        char_freq = {}
        for char in text.lower():
            if char.isalpha():
                char_freq[char] = char_freq.get(char, 0) + 1
        
        # Create a 128-dimensional vector based on various text features
        embedding = [0.0] * 128
        
        # Character frequency features (first 26 dimensions)
        for i, char in enumerate('abcdefghijklmnopqrstuvwxyz'):
            if i < 26:
                embedding[i] = char_freq.get(char, 0) / max(len(text), 1)
        
        # Word length features
        words = text.split()
        if words:
            embedding[26] = len(words) / 100.0  # Number of words
            embedding[27] = sum(len(word) for word in words) / len(words) / 10.0  # Average word length
        
        # Basic n-gram features (simplified)
        bigrams = [text[i:i+2] for i in range(len(text)-1)]
        common_bigrams = ['th', 'he', 'in', 'er', 'an', 're', 'ed', 'nd', 'on', 'en']
        for i, bigram in enumerate(common_bigrams):
            if i < 10:
                embedding[28 + i] = bigrams.count(bigram) / max(len(bigrams), 1)
        
        # Text length features
        embedding[38] = len(text) / 1000.0  # Text length
        embedding[39] = len(text.split('.')) / 10.0  # Sentence count
        
        # Dental-specific keywords (for domain relevance)
        dental_keywords = ['tooth', 'teeth', 'dental', 'gum', 'cavity', 'filling', 'crown', 'root', 'cleaning', 'hygiene']
        for i, keyword in enumerate(dental_keywords):
            if i < 10:
                embedding[40 + i] = text.lower().count(keyword) / max(len(words), 1)
        
        # Normalize the embedding
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = [x / norm for x in embedding]
        
        return embedding
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts in batch (more efficient than individual calls)"""
        try:
            if self.is_available:
                # Use SentenceTransformers batch processing for efficiency
                cleaned_texts = [self._clean_text(text) for text in texts]
                embeddings = self.model.encode(cleaned_texts, convert_to_tensor=False, batch_size=32)
                return embeddings.tolist()
            else:
                # Fallback to individual processing
                embeddings = []
                for text in texts:
                    embedding = self.generate_embedding(text)
                    embeddings.append(embedding)
                return embeddings
            
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise
    
    def _clean_text(self, text: str) -> str:
        """Clean and prepare text for embedding"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Truncate if too long (SentenceTransformers typically handle ~512 tokens)
        if self.is_available:
            # More accurate token-based truncation for transformer models
            words = text.split()
            if len(words) > self.max_tokens:
                text = ' '.join(words[:self.max_tokens])
                logger.warning(f"Text truncated to {self.max_tokens} tokens")
        else:
            # Character-based truncation for basic approach
            max_chars = self.max_tokens * 4
            if len(text) > max_chars:
                text = text[:max_chars]
                logger.warning(f"Text truncated to {max_chars} characters")
        
        return text
    
    def embed_qa_pair(self, question: str, answer: str) -> List[float]:
        """Generate embedding for a QA pair by combining question and answer"""
        combined_text = f"Q: {question}\nA: {answer}"
        return self.generate_embedding(combined_text)
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            a = np.array(vec1)
            b = np.array(vec2)
            
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
            
        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {e}")
            return 0.0
    
    def store_embedding(self, db: Session, question: str, answer: str, 
                       category: str = None, source: str = "user_defined", 
                       source_url: str = None) -> KnowledgeBase:
        """Store QA pair with embedding in database"""
        try:
            # Generate embedding
            embedding = self.embed_qa_pair(question, answer)
            
            # Create knowledge base entry
            kb_entry = KnowledgeBase(
                question=question,
                answer=answer,
                category=category,
                source=source,
                source_url=source_url,
                embedding_vector=json.dumps(embedding),
                embedding_model=self.model_name
            )
            
            db.add(kb_entry)
            db.commit()
            db.refresh(kb_entry)
            
            logger.info(f"Stored QA pair with embedding: {kb_entry.id}")
            return kb_entry
            
        except Exception as e:
            logger.error(f"Error storing embedding: {e}")
            db.rollback()
            raise
    
    def update_embedding(self, db: Session, kb_id: int, question: str, answer: str) -> bool:
        """Update existing QA pair with new embedding"""
        try:
            kb_entry = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
            if not kb_entry:
                return False
            
            # Generate new embedding
            embedding = self.embed_qa_pair(question, answer)
            
            # Update entry
            kb_entry.question = question
            kb_entry.answer = answer
            kb_entry.embedding_vector = json.dumps(embedding)
            kb_entry.embedding_model = self.model_name
            kb_entry.updated_at = datetime.now()
            
            db.commit()
            logger.info(f"Updated QA pair embedding: {kb_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating embedding: {e}")
            db.rollback()
            return False
    
    def get_embedding_from_db(self, kb_entry: KnowledgeBase) -> List[float]:
        """Extract embedding vector from database entry"""
        try:
            if not kb_entry.embedding_vector:
                return []
            
            return json.loads(kb_entry.embedding_vector)
            
        except Exception as e:
            logger.error(f"Error parsing embedding from DB: {e}")
            return []
    
    def batch_store_embeddings(self, db: Session, qa_pairs: List[Dict]) -> List[KnowledgeBase]:
        """Store multiple QA pairs with embeddings in batch"""
        try:
            # Prepare texts for batch embedding
            texts = [f"Q: {pair['question']}\nA: {pair['answer']}" for pair in qa_pairs]
            
            # Generate embeddings in batch
            embeddings = self.generate_embeddings_batch(texts)
            
            # Create database entries
            kb_entries = []
            for i, pair in enumerate(qa_pairs):
                kb_entry = KnowledgeBase(
                    question=pair['question'],
                    answer=pair['answer'],
                    category=pair.get('category'),
                    source=pair.get('source', 'user_defined'),
                    source_url=pair.get('source_url'),
                    embedding_vector=json.dumps(embeddings[i]),
                    embedding_model=self.model_name
                )
                kb_entries.append(kb_entry)
            
            # Batch insert
            db.add_all(kb_entries)
            db.commit()
            
            logger.info(f"Stored {len(kb_entries)} QA pairs with embeddings")
            return kb_entries
            
        except Exception as e:
            logger.error(f"Error batch storing embeddings: {e}")
            db.rollback()
            raise
    
    def rebuild_embeddings(self, db: Session) -> int:
        """Rebuild all embeddings in the database"""
        try:
            # Get all active knowledge base entries
            kb_entries = db.query(KnowledgeBase).filter(KnowledgeBase.is_active == True).all()
            
            if not kb_entries:
                logger.info("No knowledge base entries to rebuild")
                return 0
            
            # Prepare texts for batch embedding
            texts = [f"Q: {entry.question}\nA: {entry.answer}" for entry in kb_entries]
            
            # Generate embeddings in batch
            embeddings = self.generate_embeddings_batch(texts)
            
            # Update entries
            for i, entry in enumerate(kb_entries):
                entry.embedding_vector = json.dumps(embeddings[i])
                entry.embedding_model = self.model_name
                entry.updated_at = datetime.utcnow()
            
            db.commit()
            logger.info(f"Rebuilt embeddings for {len(kb_entries)} entries")
            return len(kb_entries)
            
        except Exception as e:
            logger.error(f"Error rebuilding embeddings: {e}")
            db.rollback()
            raise


# Global instance
_embeddings_service = None

def get_embeddings_service() -> EmbeddingsService:
    """Get global embeddings service instance"""
    global _embeddings_service
    if _embeddings_service is None:
        _embeddings_service = EmbeddingsService()
    return _embeddings_service