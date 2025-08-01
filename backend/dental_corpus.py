from typing import List, Dict, Optional
from sqlalchemy.orm import Session
import logging
from datetime import datetime

from qa_management import get_qa_manager

logger = logging.getLogger(__name__)

class DentalCorpusLoader:
    """Loader for general dentistry knowledge corpus"""
    
    def __init__(self):
        self.qa_manager = get_qa_manager()
    
    def get_dental_corpus(self) -> List[Dict]:
        """Get general dentistry QA pairs"""
        return [
            {
                'question': 'How often should I brush my teeth?',
                'answer': 'You should brush your teeth at least twice a day, preferably after meals. Use fluoride toothpaste and brush for at least 2 minutes each time.',
                'category': 'oral_hygiene',
                'source': 'dental_corpus'
            },
            {
                'question': 'What is the best way to floss?',
                'answer': 'Use about 18 inches of floss, wind most around your middle fingers, and gently guide it between your teeth. Curve the floss into a C-shape against each tooth and gently slide it under the gumline.',
                'category': 'oral_hygiene',
                'source': 'dental_corpus'
            },
            {
                'question': 'How often should I visit the dentist?',
                'answer': 'Most people should visit the dentist every 6 months for regular checkups and cleanings. However, some people may need more frequent visits based on their oral health needs.',
                'category': 'preventive_care',
                'source': 'dental_corpus'
            },
            {
                'question': 'What causes tooth decay?',
                'answer': 'Tooth decay is caused by bacteria in your mouth that produce acids when they feed on sugars and starches from food. These acids attack tooth enamel, leading to cavities.',
                'category': 'dental_conditions',
                'source': 'dental_corpus'
            },
            {
                'question': 'What should I do if I have a toothache?',
                'answer': 'For a toothache, rinse with warm water, use dental floss to remove trapped food, and take over-the-counter pain relievers as directed. See a dentist as soon as possible.',
                'category': 'emergency_care',
                'source': 'dental_corpus'
            },
            {
                'question': 'What are the signs of gum disease?',
                'answer': 'Signs of gum disease include red, swollen, or bleeding gums, persistent bad breath, receding gums, and loose teeth. Early treatment is important to prevent progression.',
                'category': 'dental_conditions',
                'source': 'dental_corpus'
            },
            {
                'question': 'Are dental X-rays safe?',
                'answer': 'Yes, dental X-rays are safe. They use very low levels of radiation, and modern digital X-rays use even less. The benefits of early detection far outweigh the minimal risks.',
                'category': 'dental_procedures',
                'source': 'dental_corpus'
            },
            {
                'question': 'What is a root canal?',
                'answer': 'A root canal is a procedure to treat infected or severely damaged tooth pulp. The infected tissue is removed, the tooth is cleaned and disinfected, then filled and sealed.',
                'category': 'dental_procedures',
                'source': 'dental_corpus'
            },
            {
                'question': 'When should children first visit the dentist?',
                'answer': 'Children should have their first dental visit by their first birthday or within 6 months of their first tooth appearing, whichever comes first.',
                'category': 'pediatric_dentistry',
                'source': 'dental_corpus'
            },
            {
                'question': 'What foods are bad for teeth?',
                'answer': 'Sugary and acidic foods like candy, soda, citrus fruits, and sticky foods can harm teeth. Limit these foods and rinse with water after consuming them.',
                'category': 'nutrition',
                'source': 'dental_corpus'
            },
            {
                'question': 'What foods are good for teeth?',
                'answer': 'Calcium-rich foods like dairy products, leafy greens, and almonds strengthen teeth. Crunchy fruits and vegetables help clean teeth naturally.',
                'category': 'nutrition',
                'source': 'dental_corpus'
            },
            {
                'question': 'How do I know if I need a filling?',
                'answer': 'Signs you may need a filling include tooth sensitivity, pain when biting, visible holes or pits in teeth, or dark spots on teeth. A dentist can confirm through examination.',
                'category': 'dental_procedures',
                'source': 'dental_corpus'
            },
            {
                'question': 'What is teeth whitening?',
                'answer': 'Teeth whitening is a cosmetic procedure that lightens teeth and removes stains. It can be done professionally at a dental office or at home with dentist-approved products.',
                'category': 'cosmetic_dentistry',
                'source': 'dental_corpus'
            },
            {
                'question': 'What are dental implants?',
                'answer': 'Dental implants are artificial tooth roots made of titanium that are surgically placed into the jawbone to replace missing teeth. They provide a strong foundation for crowns or dentures.',
                'category': 'restorative_dentistry',
                'source': 'dental_corpus'
            },
            {
                'question': 'What is the difference between a crown and a filling?',
                'answer': 'A filling repairs small cavities by filling the hole with material. A crown covers the entire visible portion of a damaged tooth, providing more extensive protection.',
                'category': 'dental_procedures',
                'source': 'dental_corpus'
            },
            {
                'question': 'How can I prevent bad breath?',
                'answer': 'Prevent bad breath by brushing and flossing regularly, cleaning your tongue, staying hydrated, avoiding tobacco, and seeing your dentist regularly.',
                'category': 'oral_hygiene',
                'source': 'dental_corpus'
            },
            {
                'question': 'What should I do if I knock out a tooth?',
                'answer': 'If you knock out a tooth, handle it by the crown (not the root), rinse gently if dirty, try to reinsert it, or keep it in milk. See a dentist immediately.',
                'category': 'emergency_care',
                'source': 'dental_corpus'
            },
            {
                'question': 'Are electric toothbrushes better than manual ones?',
                'answer': 'Electric toothbrushes can be more effective at removing plaque and reducing gingivitis, especially for people with limited mobility. However, proper technique is key with both types.',
                'category': 'oral_hygiene',
                'source': 'dental_corpus'
            },
            {
                'question': 'What is dry mouth and how is it treated?',
                'answer': 'Dry mouth occurs when salivary glands don\'t produce enough saliva. Treatment includes staying hydrated, using saliva substitutes, and addressing underlying causes.',
                'category': 'dental_conditions',
                'source': 'dental_corpus'
            },
            {
                'question': 'Can pregnancy affect my dental health?',
                'answer': 'Yes, pregnancy can increase the risk of gum disease due to hormonal changes. Pregnant women should maintain good oral hygiene and have regular dental checkups.',
                'category': 'special_populations',
                'source': 'dental_corpus'
            },
            {
                'question': 'What are wisdom teeth?',
                'answer': 'Wisdom teeth are the third set of molars that usually emerge in late teens or early twenties. They often need to be removed if there isn\'t enough room in the mouth.',
                'category': 'oral_surgery',
                'source': 'dental_corpus'
            },
            {
                'question': 'How long do dental treatments take to heal?',
                'answer': 'Healing time varies by procedure. Simple fillings heal immediately, extractions take 1-2 weeks, and implants can take 3-6 months to fully integrate.',
                'category': 'dental_procedures',
                'source': 'dental_corpus'
            },
            {
                'question': 'What is periodontal disease?',
                'answer': 'Periodontal disease is a serious gum infection that damages the soft tissue and bone supporting teeth. It can lead to tooth loss if left untreated.',
                'category': 'dental_conditions',
                'source': 'dental_corpus'
            },
            {
                'question': 'Should I use mouthwash?',
                'answer': 'Mouthwash can be a helpful addition to brushing and flossing, especially therapeutic mouthwashes that reduce bacteria and strengthen teeth. It doesn\'t replace brushing and flossing.',
                'category': 'oral_hygiene',
                'source': 'dental_corpus'
            },
            {
                'question': 'What are the different types of braces?',
                'answer': 'Types of braces include traditional metal braces, ceramic braces, lingual braces (behind teeth), and clear aligners like Invisalign. Each has different advantages.',
                'category': 'orthodontics',
                'source': 'dental_corpus'
            },
            {
                'question': 'How can I reduce dental anxiety?',
                'answer': 'To reduce dental anxiety, communicate with your dentist about your fears, practice relaxation techniques, consider sedation options, and schedule appointments at times when you feel most comfortable.',
                'category': 'patient_care',
                'source': 'dental_corpus'
            },
            {
                'question': 'What is TMJ disorder?',
                'answer': 'TMJ disorder affects the temporomandibular joint connecting your jaw to your skull. Symptoms include jaw pain, clicking sounds, and difficulty opening the mouth.',
                'category': 'dental_conditions',
                'source': 'dental_corpus'
            },
            {
                'question': 'How do I care for my teeth after oral surgery?',
                'answer': 'After oral surgery, follow your dentist\'s instructions, avoid spitting or using straws, eat soft foods, avoid smoking, and take prescribed medications as directed.',
                'category': 'post_treatment_care',
                'source': 'dental_corpus'
            },
            {
                'question': 'What is fluoride and why is it important?',
                'answer': 'Fluoride is a mineral that helps prevent tooth decay by strengthening tooth enamel and making teeth more resistant to acid attacks from bacteria.',
                'category': 'preventive_care',
                'source': 'dental_corpus'
            },
            {
                'question': 'Can diabetes affect my oral health?',
                'answer': 'Yes, diabetes can increase the risk of gum disease and other oral health problems. People with diabetes should maintain excellent oral hygiene and have regular dental checkups.',
                'category': 'special_populations',
                'source': 'dental_corpus'
            }
        ]
    
    def load_corpus(self, db: Session) -> bool:
        """Load dental corpus into knowledge base"""
        try:
            logger.info("Loading dental corpus into knowledge base")
            
            # Get corpus data
            corpus_data = self.get_dental_corpus()
            
            # Check if corpus is already loaded
            existing_count = db.query(
                self.qa_manager.embeddings_service.KnowledgeBase
            ).filter(
                self.qa_manager.embeddings_service.KnowledgeBase.source == 'dental_corpus'
            ).count()
            
            if existing_count > 0:
                logger.info(f"Dental corpus already loaded ({existing_count} entries)")
                return True
            
            # Load corpus using batch create
            kb_entries = self.qa_manager.batch_create_qa_pairs(db, corpus_data)
            
            if kb_entries:
                logger.info(f"Successfully loaded {len(kb_entries)} dental corpus entries")
                return True
            else:
                logger.error("Failed to load dental corpus")
                return False
                
        except Exception as e:
            logger.error(f"Error loading dental corpus: {e}")
            return False
    
    def update_corpus(self, db: Session) -> bool:
        """Update existing dental corpus entries"""
        try:
            logger.info("Updating dental corpus")
            
            # Get current corpus data
            corpus_data = self.get_dental_corpus()
            
            # Get existing entries
            existing_entries = db.query(
                self.qa_manager.embeddings_service.KnowledgeBase
            ).filter(
                self.qa_manager.embeddings_service.KnowledgeBase.source == 'dental_corpus'
            ).all()
            
            # Create lookup of existing entries by question
            existing_lookup = {entry.question: entry for entry in existing_entries}
            
            # Update existing and add new entries
            updated_count = 0
            added_count = 0
            
            for data in corpus_data:
                existing_entry = existing_lookup.get(data['question'])
                
                if existing_entry:
                    # Update existing entry
                    success = self.qa_manager.update_qa_pair(
                        db=db,
                        kb_id=existing_entry.id,
                        question=data['question'],
                        answer=data['answer'],
                        category=data['category']
                    )
                    if success:
                        updated_count += 1
                else:
                    # Add new entry
                    new_entry = self.qa_manager.create_qa_pair(
                        db=db,
                        question=data['question'],
                        answer=data['answer'],
                        category=data['category'],
                        source=data['source']
                    )
                    if new_entry:
                        added_count += 1
            
            logger.info(f"Updated {updated_count} entries, added {added_count} new entries")
            return True
            
        except Exception as e:
            logger.error(f"Error updating dental corpus: {e}")
            return False
    
    def get_corpus_stats(self, db: Session) -> Dict:
        """Get statistics about loaded dental corpus"""
        try:
            from models import KnowledgeBase
            
            # Count by category
            category_counts = {}
            categories = db.query(KnowledgeBase.category).filter(
                KnowledgeBase.source == 'dental_corpus'
            ).distinct().all()
            
            for category_tuple in categories:
                category = category_tuple[0]
                if category:
                    count = db.query(KnowledgeBase).filter(
                        KnowledgeBase.source == 'dental_corpus',
                        KnowledgeBase.category == category,
                        KnowledgeBase.is_active == True
                    ).count()
                    category_counts[category] = count
            
            total_count = db.query(KnowledgeBase).filter(
                KnowledgeBase.source == 'dental_corpus',
                KnowledgeBase.is_active == True
            ).count()
            
            return {
                'total_entries': total_count,
                'categories': category_counts,
                'source': 'dental_corpus'
            }
            
        except Exception as e:
            logger.error(f"Error getting corpus stats: {e}")
            return {}


# Global instance
_dental_corpus_loader = None

def get_dental_corpus_loader() -> DentalCorpusLoader:
    """Get global dental corpus loader instance"""
    global _dental_corpus_loader
    if _dental_corpus_loader is None:
        _dental_corpus_loader = DentalCorpusLoader()
    return _dental_corpus_loader