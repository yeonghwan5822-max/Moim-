from soynlp.word import WordExtractor
from soynlp.tokenizer import LTokenizer
import math
import logging

class OOVAnalyzer:
    def __init__(self):
        self.word_extractor = WordExtractor(
            min_frequency=5,
            min_cohesion_forward=0.05,
            min_right_branching_entropy=0.0
        )
        self.scores = {}
        
    def train(self, sentences):
        """
        Train WordExtractor with a list of strings (corpus).
        sentences: list of str
        """
        logging.info(f"Training WordExtractor on {len(sentences)} sentences...")
        self.word_extractor.train(sentences)
        self.scores = self.word_extractor.extract()
        logging.info(f"Training Complete. Found {len(self.scores)} word candidates.")

    def get_top_scored_words(self, top_k=100, score_weight=0.5):
        """
        Returns top words based on a combined score (Cohesion * (Entropy + 1))
        This is a heuristic to balance internal solidity and external boundary clarity.
        """
        scored_list = []
        for word, score in self.scores.items():
            # Standard metrics
            cohesion = score.cohesion_forward
            branching = score.right_branching_entropy
            
            # Simple combined metric
            combined_score = cohesion * (branching + 1)
            
            scored_list.append({
                'word': word,
                'cohesion': cohesion,
                'branching_entropy': branching,
                'combined_score': combined_score,
                'frequency': score.leftside_frequency
            })
            
        # Sort by combined score desc
        scored_list.sort(key=lambda x: x['combined_score'], reverse=True)
        return scored_list[:top_k]

    def tokenize(self, text):
        """
        Tokenize new text using the trained scores (LTokenizer).
        """
        if not self.scores:
            raise ValueError("Analyzer not trained yet.")
        
        # Use cohesion scores for Tokenization
        cohesion_scores = {word: score.cohesion_forward for word, score in self.scores.items()}
        tokenizer = LTokenizer(scores=cohesion_scores)
        return tokenizer.tokenize(text)
