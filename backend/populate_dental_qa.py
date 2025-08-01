"""
Populate the AI Dentist knowledge base with comprehensive dental Q&A pairs.
This script adds basic dental knowledge for the RAG system.
"""

import asyncio
import aiohttp
import json
from typing import List, Dict

# Basic dental Q&A knowledge base
DENTAL_QA_PAIRS = [
    # General Dental Care
    {
        "question": "How often should I brush my teeth?",
        "answer": "You should brush your teeth at least twice a day - once in the morning and once before bed. Ideally, brush after every meal if possible. Use fluoride toothpaste and brush for at least 2 minutes each time.",
        "category": "oral_hygiene",
        "source": "user_defined"
    },
    {
        "question": "How often should I floss?",
        "answer": "You should floss at least once a day, preferably before bedtime. Flossing removes plaque and food particles between teeth that your toothbrush can't reach. If you're new to flossing, your gums may bleed initially, but this should stop as your gums become healthier.",
        "category": "oral_hygiene",
        "source": "user_defined"
    },
    {
        "question": "What type of toothbrush should I use?",
        "answer": "Use a soft-bristled toothbrush to avoid damaging your gums and tooth enamel. Electric toothbrushes can be more effective at removing plaque than manual ones. Replace your toothbrush every 3-4 months or sooner if the bristles become frayed.",
        "category": "oral_hygiene",
        "source": "user_defined"
    },
    {
        "question": "How often should I visit the dentist?",
        "answer": "Most people should visit the dentist every 6 months for regular checkups and cleanings. However, some individuals may need more frequent visits depending on their oral health condition. Your dentist will recommend the best schedule for you.",
        "category": "preventive_care",
        "source": "user_defined"
    },
    {
        "question": "What should I expect during a dental cleaning?",
        "answer": "During a dental cleaning, a hygienist will remove plaque and tartar buildup, polish your teeth, and may apply fluoride treatment. The dentist will examine your teeth and gums for signs of decay, gum disease, or other problems. X-rays may be taken if needed.",
        "category": "preventive_care",
        "source": "user_defined"
    },

    # Dental Problems & Conditions
    {
        "question": "What causes tooth decay?",
        "answer": "Tooth decay is caused by bacteria in your mouth that feed on sugars and starches from food and drinks. These bacteria produce acids that attack tooth enamel. Poor oral hygiene, frequent snacking, sugary drinks, and lack of fluoride increase your risk of decay.",
        "category": "dental_conditions",
        "source": "user_defined"
    },
    {
        "question": "What are the signs of gum disease?",
        "answer": "Early signs of gum disease include red, swollen, or tender gums, bleeding when brushing or flossing, persistent bad breath, and receding gums. Advanced gum disease may cause loose teeth, painful chewing, and pus between teeth and gums.",
        "category": "dental_conditions",
        "source": "user_defined"
    },
    {
        "question": "Why do my teeth hurt when I eat cold or hot foods?",
        "answer": "Tooth sensitivity to hot or cold foods usually indicates exposed tooth roots or worn enamel. This can be caused by gum recession, tooth grinding, aggressive brushing, or tooth decay. Using desensitizing toothpaste and avoiding acidic foods can help, but see your dentist for proper diagnosis.",
        "category": "dental_conditions",
        "source": "user_defined"
    },
    {
        "question": "What should I do if I have a toothache?",
        "answer": "For immediate relief, rinse with warm salt water, take over-the-counter pain medication as directed, and apply a cold compress to the outside of your cheek. Avoid placing aspirin directly on the tooth. See your dentist as soon as possible, as toothaches often indicate serious problems.",
        "category": "emergency_care",
        "source": "user_defined"
    },
    {
        "question": "What should I do if I knock out a tooth?",
        "answer": "If a permanent tooth is knocked out, handle it by the crown (not the root), rinse gently if dirty, and try to place it back in the socket. If that's not possible, keep it in milk or saliva. See a dentist immediately - within 30 minutes if possible for the best chance of saving the tooth.",
        "category": "emergency_care",
        "source": "user_defined"
    },

    # Dental Procedures
    {
        "question": "What is a dental filling?",
        "answer": "A dental filling is used to repair a tooth damaged by decay. The dentist removes the decayed portion of the tooth and fills the area with material such as composite resin, porcelain, or silver amalgam. Fillings restore the tooth's function and prevent further decay.",
        "category": "restorative_dentistry",
        "source": "user_defined"
    },
    {
        "question": "How long do dental fillings last?",
        "answer": "The lifespan of dental fillings varies by material: composite fillings typically last 5-7 years, silver amalgam fillings can last 10-15 years, and porcelain fillings may last 15+ years. Proper oral hygiene and regular dental visits help extend the life of your fillings.",
        "category": "restorative_dentistry",
        "source": "user_defined"
    },
    {
        "question": "What is a root canal?",
        "answer": "A root canal is a procedure to treat infected or severely damaged tooth pulp. The dentist removes the infected tissue, cleans and disinfects the root canals, then fills and seals the space. A crown is usually placed over the tooth to restore its strength and appearance.",
        "category": "dental_procedures",
        "source": "user_defined"
    },
    {
        "question": "Do root canals hurt?",
        "answer": "Modern root canal procedures are typically no more painful than getting a large filling. Local anesthesia is used to numb the area during treatment. Some mild discomfort may occur for a few days after the procedure, which can be managed with over-the-counter pain medication.",
        "category": "dental_procedures",
        "source": "user_defined"
    },
    {
        "question": "What is a dental crown?",
        "answer": "A dental crown is a tooth-shaped cap that covers a damaged tooth to restore its size, shape, strength, and appearance. Crowns are used for teeth with large fillings, after root canal treatment, to cover dental implants, or to improve the appearance of misshapen or discolored teeth.",
        "category": "restorative_dentistry",
        "source": "user_defined"
    },

    # Cosmetic Dentistry
    {
        "question": "What is teeth whitening?",
        "answer": "Teeth whitening is a cosmetic procedure that lightens teeth and removes stains and discoloration. It can be done in-office with professional-strength bleaching agents or at home with custom trays and whitening gel. Results typically last 1-3 years depending on diet and habits.",
        "category": "cosmetic_dentistry",
        "source": "user_defined"
    },
    {
        "question": "Are teeth whitening procedures safe?",
        "answer": "Professional teeth whitening is generally safe when performed or supervised by a dentist. Some people may experience temporary tooth sensitivity or gum irritation. Over-the-counter products are less effective and may cause more sensitivity if not used properly.",
        "category": "cosmetic_dentistry",
        "source": "user_defined"
    },
    {
        "question": "What are dental veneers?",
        "answer": "Dental veneers are thin, custom-made shells that cover the front surface of teeth to improve their appearance. They can correct discolored, worn, chipped, or misaligned teeth. Veneers are made from porcelain or composite resin and are permanently bonded to your teeth.",
        "category": "cosmetic_dentistry",
        "source": "user_defined"
    },

    # Pediatric Dentistry
    {
        "question": "When should children first visit the dentist?",
        "answer": "Children should have their first dental visit by age 1 or within 6 months of their first tooth appearing. Early visits help establish good oral health habits, allow the dentist to monitor tooth development, and help children become comfortable with dental care.",
        "category": "pediatric_dentistry",
        "source": "user_defined"
    },
    {
        "question": "How can I help my child maintain good oral hygiene?",
        "answer": "Help young children brush their teeth twice daily, supervise brushing until age 6-8, limit sugary snacks and drinks, encourage drinking water, and schedule regular dental visits. Make oral care fun with colorful toothbrushes, flavored toothpaste, and positive reinforcement.",
        "category": "pediatric_dentistry",
        "source": "user_defined"
    },
    {
        "question": "What are dental sealants?",
        "answer": "Dental sealants are thin, protective coatings applied to the chewing surfaces of back teeth (molars) to prevent decay. They're especially beneficial for children and teenagers, as they seal the deep grooves where food particles and bacteria can accumulate.",
        "category": "preventive_care",
        "source": "user_defined"
    },

    # Orthodontics
    {
        "question": "When should I consider braces?",
        "answer": "Consider braces if you have crooked teeth, crowded teeth, gaps between teeth, overbite, underbite, or crossbite. The best time for children to get braces is typically between ages 10-14, but adults can also benefit from orthodontic treatment at any age.",
        "category": "orthodontics",
        "source": "user_defined"
    },
    {
        "question": "What are the different types of braces?",
        "answer": "Common types include traditional metal braces, ceramic (clear) braces, lingual braces (behind teeth), and clear aligners like Invisalign. Each type has advantages and disadvantages regarding appearance, comfort, treatment time, and cost. Your orthodontist will recommend the best option for your needs.",
        "category": "orthodontics",
        "source": "user_defined"
    },
    {
        "question": "How long do I need to wear braces?",
        "answer": "Treatment time typically ranges from 18 months to 3 years, depending on the complexity of your case, your age, and how well you follow instructions. After braces are removed, you'll need to wear a retainer to maintain your new smile.",
        "category": "orthodontics",
        "source": "user_defined"
    },

    # Nutrition and Diet
    {
        "question": "What foods are bad for my teeth?",
        "answer": "Limit sugary and starchy foods like candy, cookies, chips, and soft drinks. Acidic foods and drinks like citrus fruits, wine, and soda can erode tooth enamel. Sticky foods like dried fruit and gummy candies cling to teeth and feed bacteria.",
        "category": "nutrition",
        "source": "user_defined"
    },
    {
        "question": "What foods are good for dental health?",
        "answer": "Foods rich in calcium (dairy products, leafy greens), phosphorus (eggs, fish, nuts), and vitamin C (citrus fruits, berries) support dental health. Crunchy fruits and vegetables help clean teeth naturally. Drinking plenty of water helps rinse away food particles and bacteria.",
        "category": "nutrition",
        "source": "user_defined"
    },
    {
        "question": "Is chewing gum good for teeth?",
        "answer": "Sugar-free gum can be beneficial for oral health. Chewing stimulates saliva production, which helps neutralize acids and wash away food particles. Look for gum with xylitol, which may help reduce harmful bacteria. Avoid sugary gum, which can contribute to tooth decay.",
        "category": "nutrition",
        "source": "user_defined"
    },

    # Clinic-Specific Information
    {
        "question": "What services do you offer?",
        "answer": "We offer comprehensive dental services including routine cleanings and exams, fillings, crowns, root canals, tooth extractions, teeth whitening, dental implants, orthodontics, and emergency dental care. Our experienced team is committed to providing quality care in a comfortable environment.",
        "category": "office_information",
        "source": "user_defined"
    },
    {
        "question": "How do I schedule an appointment?",
        "answer": "You can schedule an appointment by calling our office, using our online booking system on our website, or visiting us in person. We try to accommodate urgent needs and offer flexible scheduling options including evening and weekend appointments.",
        "category": "appointments",
        "source": "user_defined"
    },
    {
        "question": "What should I bring to my first appointment?",
        "answer": "Please bring a valid ID, your insurance card (if applicable), a list of current medications, your medical and dental history, and any previous dental X-rays or records. Arrive 15 minutes early to complete any necessary paperwork.",
        "category": "first_visit",
        "source": "user_defined"
    },
    {
        "question": "Do you accept insurance?",
        "answer": "We accept most major dental insurance plans. Our staff will help verify your benefits and explain your coverage. We also offer flexible payment options and financing plans for treatments not covered by insurance. Please contact us to verify your specific plan.",
        "category": "insurance",
        "source": "user_defined"
    },
    {
        "question": "What are your office hours?",
        "answer": "Our office hours are Monday through Friday 8:00 AM to 6:00 PM, and Saturday 9:00 AM to 3:00 PM. We're closed on Sundays. We also offer emergency services for urgent dental problems outside regular hours.",
        "category": "office_information",
        "source": "user_defined"
    },
    {
        "question": "Do you offer emergency dental services?",
        "answer": "Yes, we provide emergency dental services for urgent problems like severe toothaches, broken teeth, knocked-out teeth, and dental trauma. If you have a dental emergency outside office hours, please call our emergency line for instructions.",
        "category": "emergency_care",
        "source": "user_defined"
    },

    # Payment and Pricing
    {
        "question": "What payment methods do you accept?",
        "answer": "We accept cash, credit cards (Visa, MasterCard, American Express), debit cards, and checks. We also offer financing options through CareCredit and other healthcare financing companies to help make treatment more affordable.",
        "category": "payment",
        "source": "user_defined"
    },
    {
        "question": "How much does a dental cleaning cost?",
        "answer": "The cost of a routine dental cleaning typically ranges from $120-180, depending on your specific needs. If you have insurance, much of this cost may be covered. We'll provide a detailed estimate before any treatment and help you understand your insurance benefits.",
        "category": "pricing",
        "source": "user_defined"
    },
    {
        "question": "How much does a filling cost?",
        "answer": "Filling costs vary based on the size, location, and material used. Composite (tooth-colored) fillings typically range from $150-350 per tooth. We'll discuss your options and provide a cost estimate before beginning treatment.",
        "category": "pricing",
        "source": "user_defined"
    },

    # Special Conditions
    {
        "question": "Is it safe to have dental work during pregnancy?",
        "answer": "Routine dental care is safe and important during pregnancy. The second trimester is usually the best time for dental treatment. Always inform your dentist if you're pregnant or trying to conceive. Some procedures may be postponed until after delivery for your comfort and safety.",
        "category": "special_populations",
        "source": "user_defined"
    },
    {
        "question": "How does diabetes affect oral health?",
        "answer": "Diabetes increases the risk of gum disease, dry mouth, and slow healing after dental procedures. High blood sugar can worsen gum disease, and gum disease can make blood sugar harder to control. Regular dental visits and good oral hygiene are especially important for diabetic patients.",
        "category": "special_populations",
        "source": "user_defined"
    },
    {
        "question": "Can I get dental work if I have a heart condition?",
        "answer": "Most dental procedures are safe for people with heart conditions, but it's important to inform your dentist about your condition and medications. Some patients may need antibiotic premedication before certain procedures. We'll coordinate with your physician when necessary.",
        "category": "special_populations",
        "source": "user_defined"
    }
]

async def add_qa_pairs(api_base_url: str = "http://localhost:8000"):
    """Add all Q&A pairs to the knowledge base via API calls."""
    
    async with aiohttp.ClientSession() as session:
        successful_adds = 0
        failed_adds = 0
        
        print(f"Adding {len(DENTAL_QA_PAIRS)} Q&A pairs to the knowledge base...")
        
        for i, qa_pair in enumerate(DENTAL_QA_PAIRS, 1):
            try:
                async with session.post(
                    f"{api_base_url}/api/chatbot/qa",
                    json=qa_pair,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        successful_adds += 1
                        print(f"✅ {i}/{len(DENTAL_QA_PAIRS)}: Added - {qa_pair['question'][:60]}...")
                    else:
                        failed_adds += 1
                        error_text = await response.text()
                        print(f"❌ {i}/{len(DENTAL_QA_PAIRS)}: Failed - {qa_pair['question'][:60]}... (Error: {response.status})")
                        
            except Exception as e:
                failed_adds += 1
                print(f"❌ {i}/{len(DENTAL_QA_PAIRS)}: Exception - {qa_pair['question'][:60]}... (Error: {str(e)})")
        
        print(f"\n📊 Summary:")
        print(f"✅ Successfully added: {successful_adds}")
        print(f"❌ Failed to add: {failed_adds}")
        print(f"📝 Total attempted: {len(DENTAL_QA_PAIRS)}")
        
        # Rebuild the vector index after adding all entries
        if successful_adds > 0:
            print(f"\n🔧 Rebuilding vector index...")
            try:
                async with session.post(f"{api_base_url}/api/chatbot/system/rebuild-index") as response:
                    if response.status == 200:
                        print("✅ Vector index rebuilt successfully!")
                    else:
                        print(f"❌ Failed to rebuild vector index (Error: {response.status})")
            except Exception as e:
                print(f"❌ Exception rebuilding vector index: {str(e)}")

def get_qa_stats():
    """Print statistics about the Q&A pairs."""
    categories = {}
    for qa in DENTAL_QA_PAIRS:
        category = qa['category']
        categories[category] = categories.get(category, 0) + 1
    
    print("📊 Dental Q&A Knowledge Base Statistics:")
    print(f"Total Q&A pairs: {len(DENTAL_QA_PAIRS)}")
    print(f"Categories: {len(categories)}")
    print("\nQ&A pairs by category:")
    
    for category, count in sorted(categories.items()):
        category_name = category.replace('_', ' ').title()
        print(f"  • {category_name}: {count} pairs")

if __name__ == "__main__":
    import sys
    
    # Print statistics
    get_qa_stats()
    print("\n" + "="*60 + "\n")
    
    # Check if server URL is provided
    api_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    print(f"🚀 Starting to populate knowledge base at {api_url}")
    print("Make sure your backend server is running before proceeding!")
    
    # Run the async function
    asyncio.run(add_qa_pairs(api_url))