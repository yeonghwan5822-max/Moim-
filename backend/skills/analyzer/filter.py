from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

class DomainFilter:
    def __init__(self, general_corpus_path=None):
        self.vectorizer = TfidfVectorizer(
            tokenizer=lambda x: x.split(), # Expects pre-tokenized whitespace separated string
            min_df=2, 
            smooth_idf=True
        )
        self.general_corpus = [] 
        # Ideally, we load a general corpus here (e.g. news headlines file)
        # For PoC, we might assume the input batch serves as its own context vs external if available.
        
    def calculate_specificity(self, target_docs, general_docs):
        """
        Compare target domain docs vs general docs to find specific keywords.
        """
        all_docs = target_docs + general_docs
        # Label 0 for target, 1 for general (implicitly handled by order)
        
        tfidf_matrix = self.vectorizer.fit_transform(all_docs)
        feature_names = np.array(self.vectorizer.get_feature_names_out())
        
        # Calculate mean TF-IDF for the target subset
        target_matrix = tfidf_matrix[:len(target_docs)]
        mean_tfidf = np.asarray(target_matrix.mean(axis=0)).flatten()
        
        # Sort by score
        sorted_indices = mean_tfidf.argsort()[::-1]
        
        top_words = []
        for idx in sorted_indices[:100]:
            top_words.append((feature_names[idx], mean_tfidf[idx]))
            
        return top_words
