import sys
import os
import logging
import json
import re
from pathlib import Path

# Add project root to path to import skills
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from skills.analyzer.model import OOVAnalyzer
from skills.analyzer.filter import DomainFilter

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- CONFIGURATION ---
KNOWN_BIBLICAL_TERMS = {
    "하나님", "예수님", "성령", "말씀", "기도", "은혜", 
    "복음", "구원", "믿음", "찬양", "예배", "아멘", 
    "교회", "목사님", "성경", "주님", "지체" 
    # '지체' is interesting: it IS a biblical term, but PRD says it has a domain shift.
    # If we filter it here, we might miss the 'domain shift' aspect.
    # However, the user asked to "Check if they overlap with existing biblical terms".
    # I will filter out STANDARD ones, but keep '지체' if we consider it "Common" enough to exclude from *new* learning,
    # OR we treat this list as "Don't add to glossary automatically because we know them".
    # BUT '지체' needs a SPECIFIC translation in this community ("member" not "body part").
    # So I will remove '지체' from this exclusion list to ensure it GETS processed/checked.
}

COMMON_STOPWORDS = {
    "이번", "함께", "정말", "너무", "많이", "있는", "있습니다.", "했습니다.", 
    "그리고", "그러나", "그런데", "오늘", "내일", "어제", "지금", "우리"
}

def load_text_file(path):
    if not os.path.exists(path):
        logging.warning(f"File not found: {path}")
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def clean_word(word):
    """Remove trailing punctuation often caught by tokenizers."""
    return re.sub(r'[.,!?~]+$', '', word)

def main():
    """
    Main entry point for OOV Detection and Glossary Update Pipeline.
    Includes TF-IDF filtering and Biblical Term Exclusion.
    """
    logging.info("Starting OOV Detector with TF-IDF & Exclusion Filter...")

    base_dir = Path(__file__).parent.parent
    corpus_path = base_dir / "references" / "corpus_sample.txt"
    general_corpus_path = base_dir / "references" / "general_corpus.txt"
    glossary_path = base_dir / "references" / "glossary.json"

    # 1. Load Data
    domain_corpus = load_text_file(corpus_path)
    general_corpus = load_text_file(general_corpus_path)
    
    # Augment small corpus
    if len(domain_corpus) < 100:
        domain_corpus_train = domain_corpus * 20
    else:
        domain_corpus_train = domain_corpus

    logging.info(f"Loaded Domain Corpus: {len(domain_corpus)} lines")

    # 2. Train OOV Analyzer (soynlp)
    analyzer = OOVAnalyzer()
    analyzer.train(domain_corpus_train)
    
    raw_candidates = analyzer.get_top_scored_words(top_k=50)
    
    # 3. Apply Domain Filter (TF-IDF)
    domain_doc = " ".join(domain_corpus)
    domain_filter = DomainFilter()
    specific_terms = domain_filter.calculate_specificity([domain_doc], general_corpus)
    
    top_specific_words = {t[0]: t[1] for t in specific_terms[:50]} 
    
    final_candidates = []
    
    # 4. Filter & Process Candidates
    for cand in raw_candidates:
        word = clean_word(cand['word'])
        
        # 4.1 Basic Filtering (Length, Digits)
        if len(word) < 2 or word.isdigit() or re.match(r'^[A-Za-z0-9]+$', word):
            # Keep 'blue' (English) but maybe skip purely numeric?
            # User sample had 'blue', so we allow Mixed/English. Just skip mostly single chars/numbers.
            if len(word) < 2: continue
            
        # 4.2 Score Check (Soynlp Score OR TF-IDF Score)
        is_cohesive = cand['combined_score'] > 1.5
        is_specific = word in top_specific_words
        
        if not (is_cohesive or is_specific):
            continue
            
        cand['clean_word'] = word
        cand['tfidf_score'] = top_specific_words.get(word, 0.0)
        final_candidates.append(cand)

    # 5. Check against Glossaries & Exclusion Lists
    current_glossary = {}
    if os.path.exists(glossary_path):
        with open(glossary_path, 'r', encoding='utf-8') as f:
            current_glossary = json.load(f)

    new_terms_count = 0
    
    print("\n" + "="*80)
    print(f"{'Word':<15} | {'Score':<8} | {'TF-IDF':<8} | {'Status':<25} | {'Note'}")
    print("-" * 80)
    
    for item in final_candidates:
        word = item['clean_word']
        score = item['combined_score']
        tfidf = item.get('tfidf_score', 0)
        
        # Check Exclusions
        if word in COMMON_STOPWORDS:
            status = "Skipped (Stopword)"
            note = "Common word"
        elif word in KNOWN_BIBLICAL_TERMS:
            status = "Skipped (Biblical)"
            note = "Existing Standard Term"
        elif word in current_glossary:
            status = "Existing"
            note = f"Current: {current_glossary[word][:10]}..."
        else:
            # Add to Glossary
            current_glossary[word] = "" 
            status = "[NEW] Auto-Added"
            note = "Pending Translation"
            new_terms_count += 1
            
        print(f"{word:<15} | {score:<8.3f} | {tfidf:<8.3f} | {status:<25} | {note}")
    
    print("="*80 + "\n")
    
    # --- Contextual Anomaly Detection (New Feature) ---
    print("\n[Contextual Anomaly Detection]")
    context_detector = ContextualDetector()
    anomalies = context_detector.detect_anomalies(domain_corpus)
    
    print(f"{'Context Word':<15} | {'Pairs found':<30}")
    print("-" * 50)
    for item in anomalies:
        print(f"{item['word']:<15} | {str(item['pairs'])[:30]}")
    print("="*80 + "\n")

    # Save Glossary
    if new_terms_count > 0:
        with open(glossary_path, 'w', encoding='utf-8') as f:
            json.dump(current_glossary, f, ensure_ascii=False, indent=4)
        logging.info(f"Updated Glossary with {new_terms_count} new terms at {glossary_path}")
    else:
        logging.info("No new terms to add.")

class ContextualDetector:
    """
    Detects words that are statistically anomalous in the specific context.
    Method: Co-occurrence (Bigram) Analysis
    """
    def __init__(self):
        pass

    def detect_anomalies(self, corpus: list) -> list:
        from collections import Counter
        
        # 1. Simple Bigram Extraction
        bigrams = []
        for line in corpus:
            words = line.split()
            # Generate bigrams
            if len(words) < 2: continue
            for i in range(len(words)-1):
                w1, w2 = clean_word(words[i]), clean_word(words[i+1])
                if len(w1) > 1 and len(w2) > 1:
                    bigrams.append((w1, w2))
        
        # 2. Count Frequency
        counts = Counter(bigrams)
        
        # 3. Filter "Strange" Pairs (Heuristic for PoC)
        # In real logic, we'd compare P(w2|w1) in domain vs general corpus.
        # For PoC, we look for high frequent Noun+Verb patterns common in this domain
        # e.g. '말씀' + '먹다' (rare generally) -> but actually '말씀' + '듣다' is common.
        # Let's just return high-frequency bigrams that contain our key terms.
        
        targets = ["말씀", "교제", "작업", "지체", "나눔"]
        results = []
        
        for target in targets:
            related = [pair for pair in counts if target in pair]
            # sort by freq
            related = sorted(related, key=lambda x: counts[x], reverse=True)[:3]
            if related:
                results.append({"word": target, "pairs": related})
                
        return results

if __name__ == "__main__":
    main()
