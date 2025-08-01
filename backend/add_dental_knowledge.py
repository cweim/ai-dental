#!/usr/bin/env python3
"""
Add dental knowledge base entries via the API endpoints.

This script demonstrates how to add QA pairs through the same endpoints
that the frontend admin interface uses.
"""

import sys
import os
import json
from sqlalchemy.orm import Session

# Add the current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from qa_management import get_qa_manager
from dental_corpus import get_dental_corpus_loader
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_dental_corpus_entries():
    """Add all dental corpus entries to the knowledge base"""
    
    db = SessionLocal()
    try:
        qa_manager = get_qa_manager()
        corpus_loader = get_dental_corpus_loader()
        
        # Get the dental corpus
        dental_corpus = corpus_loader.get_dental_corpus()
        logger.info(f"Found {len(dental_corpus)} dental corpus entries")
        
        added_count = 0
        skipped_count = 0
        
        for entry in dental_corpus:
            try:
                # Create QA pair using the manager
                kb_entry = qa_manager.create_qa_pair(
                    db=db,
                    question=entry['question'],
                    answer=entry['answer'],
                    category=entry['category'],
                    source=entry['source']
                )
                
                if kb_entry:
                    added_count += 1
                    logger.info(f"Added: '{entry['question'][:50]}...'")
                else:
                    skipped_count += 1
                    logger.warning(f"Failed to add: '{entry['question'][:50]}...'")
                    
            except Exception as e:
                logger.error(f"Error adding entry '{entry['question'][:30]}...': {e}")
                skipped_count += 1
        
        logger.info(f"=== Summary ===")
        logger.info(f"Added: {added_count} entries")
        logger.info(f"Skipped: {skipped_count} entries")
        
        return added_count
        
    finally:
        db.close()

def add_custom_qa_pairs():
    """Add some custom dental QA pairs"""
    
    custom_qa_pairs = [
        {
            'question': 'What are your office hours?',
            'answer': 'Our office is open Monday through Friday from 8:00 AM to 6:00 PM, and Saturday from 9:00 AM to 3:00 PM. We are closed on Sundays and major holidays.',
            'category': 'office_information',
            'source': 'clinic_specific'
        },
        {
            'question': 'How do I schedule an appointment?',
            'answer': 'You can schedule an appointment by calling our office, using our online booking system, or visiting us in person. We offer same-day appointments for dental emergencies.',
            'category': 'appointments',
            'source': 'clinic_specific'
        },
        {
            'question': 'Do you accept insurance?',
            'answer': 'Yes, we accept most major dental insurance plans. Please bring your insurance card to your appointment. We can help verify your benefits and maximize your coverage.',
            'category': 'insurance',
            'source': 'clinic_specific'
        },
        {
            'question': 'What should I expect during my first visit?',
            'answer': 'Your first visit includes a comprehensive oral examination, digital X-rays if needed, professional cleaning, and consultation about any treatment needs. Please arrive 15 minutes early to complete paperwork.',
            'category': 'first_visit',
            'source': 'clinic_specific'
        },
        {
            'question': 'Do you provide emergency dental services?',
            'answer': 'Yes, we provide emergency dental services for urgent situations like severe tooth pain, knocked-out teeth, or dental trauma. Call our office immediately for emergency appointments.',
            'category': 'emergency_care',
            'source': 'clinic_specific'
        }
    ]
    
    db = SessionLocal()
    try:
        qa_manager = get_qa_manager()
        
        added_count = 0
        for entry in custom_qa_pairs:
            try:
                kb_entry = qa_manager.create_qa_pair(
                    db=db,
                    question=entry['question'],
                    answer=entry['answer'],
                    category=entry['category'],
                    source=entry['source']
                )
                
                if kb_entry:
                    added_count += 1
                    logger.info(f"Added custom: '{entry['question'][:50]}...'")
                    
            except Exception as e:
                logger.error(f"Error adding custom entry: {e}")
        
        logger.info(f"Added {added_count} custom QA pairs")
        return added_count
        
    finally:
        db.close()

def main():
    """Main function to populate knowledge base"""
    logger.info("=== Adding Dental Knowledge Base Entries ===")
    
    # Add dental corpus entries
    corpus_count = add_dental_corpus_entries()
    
    # Add custom clinic-specific entries
    custom_count = add_custom_qa_pairs()
    
    total_added = corpus_count + custom_count
    logger.info(f"=== Total Added: {total_added} QA pairs ===")
    
    if total_added > 0:
        logger.info("Knowledge base populated successfully!")
        logger.info("Next steps:")
        logger.info("1. Run the vector index rebuild: python initialize_knowledge_base.py")
        logger.info("2. Test the chatbot via the admin interface")
        logger.info("3. Add more custom QA pairs as needed")
    
    return total_added > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)