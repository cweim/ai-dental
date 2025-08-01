import os
import uuid
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from groq import Groq
import logging
from datetime import datetime
import json

from models import ChatSession, ChatMessage, KnowledgeBase
from vector_search import get_vector_search_engine
from qa_management import get_qa_manager

logger = logging.getLogger(__name__)

class ChatbotService:
    """Main chatbot service for processing queries and generating responses"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.groq_client = Groq(api_key=api_key or os.getenv("GROQ_API_KEY"))
        self.vector_search = get_vector_search_engine()
        self.qa_manager = get_qa_manager()
        self.model = "llama3-8b-8192"
        self.max_context_length = 4000
        self.similarity_threshold = 0.5
        self.top_k = 5
    
    def create_session(self, db: Session, user_id: str = None) -> ChatSession:
        """Create a new chat session"""
        try:
            session_id = str(uuid.uuid4())
            
            chat_session = ChatSession(
                session_id=session_id,
                user_id=user_id or "anonymous",
                is_active=True
            )
            
            db.add(chat_session)
            db.commit()
            db.refresh(chat_session)
            
            logger.info(f"Created new chat session: {session_id}")
            return chat_session
            
        except Exception as e:
            logger.error(f"Error creating chat session: {e}")
            db.rollback()
            raise
    
    def get_session(self, db: Session, session_id: str) -> Optional[ChatSession]:
        """Get an existing chat session"""
        try:
            return db.query(ChatSession).filter(
                ChatSession.session_id == session_id
            ).first()
            
        except Exception as e:
            logger.error(f"Error getting chat session: {e}")
            return None
    
    def end_session(self, db: Session, session_id: str) -> bool:
        """End a chat session"""
        try:
            session = self.get_session(db, session_id)
            if session:
                session.is_active = False
                session.ended_at = datetime.utcnow()
                db.commit()
                logger.info(f"Ended chat session: {session_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error ending chat session: {e}")
            db.rollback()
            return False
    
    def process_query(self, db: Session, session_id: str, query: str) -> Dict:
        """Process a user query and generate response"""
        try:
            start_time = datetime.utcnow()
            
            # Get or create session
            session = self.get_session(db, session_id)
            if not session:
                logger.error(f"Session not found: {session_id}")
                return {
                    "error": "Session not found",
                    "session_id": session_id
                }
            
            # Store user message
            user_message = ChatMessage(
                session_id=session_id,
                message_type="user",
                content=query
            )
            db.add(user_message)
            db.commit()
            
            # Search for relevant context
            search_results = self.vector_search.search_with_details(
                query=query,
                k=self.top_k,
                threshold=self.similarity_threshold,
                session_id=session_id,
                db=db
            )
            
            # Generate response using GPT
            response_data = self._generate_response(query, search_results)
            
            # Calculate response time
            response_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            # Store bot message
            bot_message = ChatMessage(
                session_id=session_id,
                message_type="bot",
                content=response_data["response"],
                sources=json.dumps(response_data.get("sources", [])),
                confidence_score=response_data.get("confidence_score"),
                response_time_ms=response_time_ms
            )
            db.add(bot_message)
            
            # Update session message count
            session.message_count += 2  # User + Bot message
            db.commit()
            
            logger.info(f"Processed query in {response_time_ms}ms for session {session_id}")
            
            return {
                "session_id": session_id,
                "response": response_data["response"],
                "sources": response_data.get("sources", []),
                "confidence_score": response_data.get("confidence_score"),
                "response_time_ms": response_time_ms,
                "search_results_count": len(search_results)
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "error": "Failed to process query",
                "session_id": session_id
            }
    
    def _generate_response(self, query: str, search_results: List[Dict]) -> Dict:
        """Generate GPT response using search results as context"""
        try:
            # Prepare context from search results
            context_parts = []
            sources = []
            
            for result in search_results:
                context_parts.append(
                    f"Q: {result['question']}\nA: {result['answer']}"
                )
                sources.append({
                    "kb_id": result["kb_id"],
                    "question": result["question"],
                    "category": result.get("category"),
                    "source": result.get("source"),
                    "similarity_score": result["similarity_score"]
                })
            
            context = "\n\n".join(context_parts)
            
            # Create prompt
            system_prompt = self._get_system_prompt()
            user_prompt = self._create_user_prompt(query, context)
            
            # Generate response
            response = self.groq_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            ai_response = response.choices[0].message.content
            
            # Calculate confidence score based on search results
            confidence_score = self._calculate_confidence_score(search_results)
            
            return {
                "response": ai_response,
                "sources": sources,
                "confidence_score": confidence_score
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                "response": "I apologize, but I'm having trouble generating a response right now. Please try again later.",
                "sources": [],
                "confidence_score": 0.0
            }
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the chatbot"""
        return """You are a friendly dental assistant chatbot for a dental practice. Your goal is to provide helpful information about general dental care and specific information about the clinic.

Communication Style:
- Be conversational and approachable, not overly formal
- Speak naturally - avoid phrases like "Thank you for reaching out" or "According to our context"
- Use phrases like "Based on what I know" or "From our clinic information" when referencing context
- Be direct and helpful while remaining professional

Your role:
1. Answer questions about dental health, procedures, and general dentistry
2. Provide clinic-specific information when available
3. Give helpful, accurate information in a friendly manner
4. Recommend consulting with a dentist for personalized medical advice

Guidelines:
- Use context information naturally in your responses
- If you don't know something, say so and suggest contacting the dental office
- Never provide specific medical diagnoses or treatment recommendations
- Keep responses informative but concise
- End with encouragement to schedule an appointment when appropriate"""
    
    def _create_user_prompt(self, query: str, context: str) -> str:
        """Create the user prompt with query and context"""
        if context:
            return f"""Here's some relevant information from our dental practice knowledge base. Use this naturally in your response - don't mention "context" directly.

INFORMATION:
{context}

USER QUESTION: {query}

Instructions:
- Answer the question using the information provided, speaking naturally
- Use phrases like "Based on what I know" or "From our clinic information" instead of referencing "context"
- Combine information from multiple sources if helpful
- If the information doesn't fully answer the question, add general dental guidance
- Be conversational and helpful, not overly formal
- Suggest contacting the dental office for specific needs"""
        else:
            return f"""The user is asking: {query}

No specific information was found in our knowledge base. Please provide helpful general dental guidance and suggest contacting the dental office for personalized advice. Be conversational and friendly."""
    
    def _calculate_confidence_score(self, search_results: List[Dict]) -> float:
        """Calculate confidence score based on search results"""
        if not search_results:
            return 0.0
        
        # Use the highest similarity score as base confidence
        max_similarity = max(result["similarity_score"] for result in search_results)
        
        # Adjust based on number of relevant results
        result_count_factor = min(len(search_results) / 3, 1.0)  # Cap at 3 results
        
        # Combine factors
        confidence = max_similarity * (0.7 + 0.3 * result_count_factor)
        
        return min(confidence, 1.0)
    
    def get_chat_history(self, db: Session, session_id: str, limit: int = 50) -> List[Dict]:
        """Get chat history for a session"""
        try:
            messages = db.query(ChatMessage).filter(
                ChatMessage.session_id == session_id
            ).order_by(ChatMessage.created_at.desc()).limit(limit).all()
            
            history = []
            for message in reversed(messages):  # Reverse to get chronological order
                history.append({
                    "message_type": message.message_type,
                    "content": message.content,
                    "sources": json.loads(message.sources) if message.sources else [],
                    "confidence_score": message.confidence_score,
                    "created_at": message.created_at.isoformat()
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting chat history: {e}")
            return []
    
    def get_session_stats(self, db: Session, session_id: str) -> Dict:
        """Get statistics for a chat session"""
        try:
            session = self.get_session(db, session_id)
            if not session:
                return {}
            
            messages = db.query(ChatMessage).filter(
                ChatMessage.session_id == session_id
            ).all()
            
            user_messages = [m for m in messages if m.message_type == "user"]
            bot_messages = [m for m in messages if m.message_type == "bot"]
            
            avg_response_time = 0
            if bot_messages:
                response_times = [m.response_time_ms for m in bot_messages if m.response_time_ms]
                if response_times:
                    avg_response_time = sum(response_times) / len(response_times)
            
            avg_confidence = 0
            if bot_messages:
                confidence_scores = [m.confidence_score for m in bot_messages if m.confidence_score]
                if confidence_scores:
                    avg_confidence = sum(confidence_scores) / len(confidence_scores)
            
            return {
                "session_id": session_id,
                "user_id": session.user_id,
                "started_at": session.started_at.isoformat(),
                "ended_at": session.ended_at.isoformat() if session.ended_at else None,
                "is_active": session.is_active,
                "total_messages": len(messages),
                "user_messages": len(user_messages),
                "bot_messages": len(bot_messages),
                "avg_response_time_ms": avg_response_time,
                "avg_confidence_score": avg_confidence
            }
            
        except Exception as e:
            logger.error(f"Error getting session stats: {e}")
            return {}
    
    def initialize_search_index(self, db: Session) -> bool:
        """Initialize the vector search index"""
        try:
            return self.vector_search.initialize_index(db)
            
        except Exception as e:
            logger.error(f"Error initializing search index: {e}")
            return False


# Global instance
_chatbot_service = None

def get_chatbot_service() -> ChatbotService:
    """Get global chatbot service instance"""
    global _chatbot_service
    if _chatbot_service is None:
        _chatbot_service = ChatbotService()
    return _chatbot_service