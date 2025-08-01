from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from pydantic import BaseModel
import logging

from database import get_db
from models import KnowledgeBase, ChatSession, ChatMessage
from chatbot_service import get_chatbot_service
from qa_management import get_qa_manager
from dental_corpus import get_dental_corpus_loader
from vector_search import get_vector_search_engine

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models for request/response
class ChatQuery(BaseModel):
    query: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    session_id: str
    response: str
    sources: List[Dict]
    confidence_score: Optional[float]
    response_time_ms: int
    search_results_count: int

class QACreate(BaseModel):
    question: str
    answer: str
    category: Optional[str] = None
    source: str = "user_defined"
    source_url: Optional[str] = None

class QAUpdate(BaseModel):
    question: str
    answer: str
    category: Optional[str] = None

class QAResponse(BaseModel):
    id: int
    question: str
    answer: str
    category: Optional[str]
    source: str
    source_url: Optional[str]
    is_active: bool
    created_at: str
    updated_at: Optional[str]
    embedding_vector: Optional[str] = None  # JSON string of embedding vector
    embedding_model: Optional[str] = None   # Model used for embedding

class SearchQuery(BaseModel):
    query: str
    k: int = 5
    threshold: float = 0.7
    category: Optional[str] = None

# Chat endpoints
@router.post("/chat", response_model=ChatResponse)
async def chat(query: ChatQuery, db: Session = Depends(get_db)):
    """Process a chat query"""
    try:
        chatbot_service = get_chatbot_service()
        
        # Create new session if none provided
        if not query.session_id:
            session = chatbot_service.create_session(db, query.user_id)
            session_id = session.session_id
        else:
            session_id = query.session_id
            # Verify session exists
            session = chatbot_service.get_session(db, session_id)
            if not session:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Session not found"
                )
        
        # Process query
        result = chatbot_service.process_query(db, session_id, query.query)
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["error"]
            )
        
        return ChatResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/chat/sessions")
async def create_chat_session(user_id: Optional[str] = None, db: Session = Depends(get_db)):
    """Create a new chat session"""
    try:
        chatbot_service = get_chatbot_service()
        session = chatbot_service.create_session(db, user_id)
        
        return {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "started_at": session.started_at.isoformat(),
            "is_active": session.is_active
        }
        
    except Exception as e:
        logger.error(f"Error creating chat session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create chat session"
        )

@router.get("/chat/sessions/{session_id}")
async def get_chat_session(session_id: str, db: Session = Depends(get_db)):
    """Get chat session details"""
    try:
        chatbot_service = get_chatbot_service()
        session = chatbot_service.get_session(db, session_id)
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        return {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "started_at": session.started_at.isoformat(),
            "ended_at": session.ended_at.isoformat() if session.ended_at else None,
            "is_active": session.is_active,
            "message_count": session.message_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chat session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.delete("/chat/sessions/{session_id}")
async def end_chat_session(session_id: str, db: Session = Depends(get_db)):
    """End a chat session"""
    try:
        chatbot_service = get_chatbot_service()
        success = chatbot_service.end_session(db, session_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        return {"message": "Session ended successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ending chat session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/chat/sessions/{session_id}/history")
async def get_chat_history(session_id: str, limit: int = 50, db: Session = Depends(get_db)):
    """Get chat history for a session"""
    try:
        chatbot_service = get_chatbot_service()
        history = chatbot_service.get_chat_history(db, session_id, limit)
        
        return {"session_id": session_id, "history": history}
        
    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/chat/sessions/{session_id}/stats")
async def get_session_stats(session_id: str, db: Session = Depends(get_db)):
    """Get statistics for a chat session"""
    try:
        chatbot_service = get_chatbot_service()
        stats = chatbot_service.get_session_stats(db, session_id)
        
        if not stats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# QA Management endpoints
@router.post("/qa", response_model=QAResponse)
async def create_qa_pair(qa: QACreate, db: Session = Depends(get_db)):
    """Create a new QA pair"""
    try:
        qa_manager = get_qa_manager()
        kb_entry = qa_manager.create_qa_pair(
            db=db,
            question=qa.question,
            answer=qa.answer,
            category=qa.category,
            source=qa.source,
            source_url=qa.source_url
        )
        
        if not kb_entry:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create QA pair"
            )
        
        return QAResponse(
            id=kb_entry.id,
            question=kb_entry.question,
            answer=kb_entry.answer,
            category=kb_entry.category,
            source=kb_entry.source,
            source_url=kb_entry.source_url,
            is_active=kb_entry.is_active,
            created_at=kb_entry.created_at.isoformat(),
            updated_at=kb_entry.updated_at.isoformat() if kb_entry.updated_at else None,
            embedding_vector=kb_entry.embedding_vector,
            embedding_model=kb_entry.embedding_model
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating QA pair: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/qa", response_model=List[QAResponse])
async def list_qa_pairs(
    category: Optional[str] = None,
    source: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """List QA pairs with optional filtering"""
    try:
        qa_manager = get_qa_manager()
        kb_entries = qa_manager.list_qa_pairs(
            db=db,
            category=category,
            source=source,
            limit=limit,
            offset=offset
        )
        
        return [
            QAResponse(
                id=entry.id,
                question=entry.question,
                answer=entry.answer,
                category=entry.category,
                source=entry.source,
                source_url=entry.source_url,
                is_active=entry.is_active,
                created_at=entry.created_at.isoformat(),
                updated_at=entry.updated_at.isoformat() if entry.updated_at else None,
                embedding_vector=entry.embedding_vector,
                embedding_model=entry.embedding_model
            )
            for entry in kb_entries
        ]
        
    except Exception as e:
        logger.error(f"Error listing QA pairs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# Move specific routes before parameterized routes to avoid conflicts
@router.post("/qa/search")
async def search_qa_pairs(search: SearchQuery, db: Session = Depends(get_db)):
    """Search QA pairs using vector similarity"""
    try:
        qa_manager = get_qa_manager()
        results = qa_manager.search_qa_pairs(
            db=db,
            query=search.query,
            k=search.k,
            threshold=search.threshold,
            category=search.category
        )
        
        return {"query": search.query, "results": results}
        
    except Exception as e:
        logger.error(f"Error searching QA pairs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/qa/categories")
async def get_categories(db: Session = Depends(get_db)):
    """Get all available categories"""
    try:
        qa_manager = get_qa_manager()
        categories = qa_manager.get_categories(db)
        
        return {"categories": categories}
        
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/qa/sources")
async def get_sources(db: Session = Depends(get_db)):
    """Get all available sources"""
    try:
        qa_manager = get_qa_manager()
        sources = qa_manager.get_sources(db)
        
        return {"sources": sources}
        
    except Exception as e:
        logger.error(f"Error getting sources: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/qa/{qa_id}", response_model=QAResponse)
async def get_qa_pair(qa_id: int, db: Session = Depends(get_db)):
    """Get a single QA pair"""
    try:
        qa_manager = get_qa_manager()
        kb_entry = qa_manager.get_qa_pair(db, qa_id)
        
        if not kb_entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="QA pair not found"
            )
        
        return QAResponse(
            id=kb_entry.id,
            question=kb_entry.question,
            answer=kb_entry.answer,
            category=kb_entry.category,
            source=kb_entry.source,
            source_url=kb_entry.source_url,
            is_active=kb_entry.is_active,
            created_at=kb_entry.created_at.isoformat(),
            updated_at=kb_entry.updated_at.isoformat() if kb_entry.updated_at else None,
            embedding_vector=kb_entry.embedding_vector,
            embedding_model=kb_entry.embedding_model
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting QA pair: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.put("/qa/{qa_id}")
async def update_qa_pair(qa_id: int, qa: QAUpdate, db: Session = Depends(get_db)):
    """Update an existing QA pair"""
    try:
        qa_manager = get_qa_manager()
        success = qa_manager.update_qa_pair(
            db=db,
            kb_id=qa_id,
            question=qa.question,
            answer=qa.answer,
            category=qa.category
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="QA pair not found"
            )
        
        return {"message": "QA pair updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating QA pair: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.delete("/qa/{qa_id}")
async def delete_qa_pair(qa_id: int, db: Session = Depends(get_db)):
    """Delete a QA pair"""
    try:
        qa_manager = get_qa_manager()
        success = qa_manager.delete_qa_pair(db, qa_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="QA pair not found"
            )
        
        return {"message": "QA pair deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting QA pair: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

# System management endpoints
@router.post("/system/initialize")
async def initialize_system(db: Session = Depends(get_db)):
    """Initialize the chatbot system"""
    try:
        chatbot_service = get_chatbot_service()
        dental_corpus_loader = get_dental_corpus_loader()
        
        # Initialize vector search index
        index_success = chatbot_service.initialize_search_index(db)
        
        # Load dental corpus if not already loaded
        corpus_success = dental_corpus_loader.load_corpus(db)
        
        return {
            "message": "System initialized successfully",
            "vector_index_initialized": index_success,
            "dental_corpus_loaded": corpus_success
        }
        
    except Exception as e:
        logger.error(f"Error initializing system: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initialize system"
        )

@router.post("/system/rebuild-index")
async def rebuild_index(db: Session = Depends(get_db)):
    """Rebuild the vector search index"""
    try:
        vector_search = get_vector_search_engine()
        success = vector_search.rebuild_index(db)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to rebuild index"
            )
        
        return {"message": "Index rebuilt successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rebuilding index: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/system/stats")
async def get_system_stats(db: Session = Depends(get_db)):
    """Get system statistics"""
    try:
        qa_manager = get_qa_manager()
        vector_search = get_vector_search_engine()
        dental_corpus_loader = get_dental_corpus_loader()
        
        qa_stats = qa_manager.get_stats(db)
        vector_stats = vector_search.get_stats()
        corpus_stats = dental_corpus_loader.get_corpus_stats(db)
        
        # Get session stats
        total_sessions = db.query(ChatSession).count()
        active_sessions = db.query(ChatSession).filter(ChatSession.is_active == True).count()
        total_messages = db.query(ChatMessage).count()
        
        return {
            "qa_management": qa_stats,
            "vector_search": vector_stats,
            "dental_corpus": corpus_stats,
            "chat_sessions": {
                "total_sessions": total_sessions,
                "active_sessions": active_sessions,
                "total_messages": total_messages
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )