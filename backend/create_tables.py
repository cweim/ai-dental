from sqlalchemy import create_engine
from database import Base
from models import (
    User, Treatment, Appointment, ChatbotQA, EmailLog, EmailTemplate, 
    EmailPreference, KnowledgeBase, ChatSession, ChatMessage, 
    VectorSearchLog, ClinicSetting
)
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://username:password@localhost:5432/ai_dentist")

def create_tables():
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

if __name__ == "__main__":
    create_tables()