import os
import sys
import json
import logging
import deepl
import chromadb
from chromadb.utils import embedding_functions
from typing import Dict, Optional
from dotenv import load_dotenv
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load Env
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

class TranslatorEngine:
    def __init__(self, glossary_path: str, corpus_path: str, db_path: str = "./data/chroma_db"):
        self.glossary_path = glossary_path
        self.corpus_path = corpus_path
        
        # 1. Initialize DeepL
        self.auth_key = os.getenv("DEEPL_AUTH_KEY")
        self.translator = None
        if self.auth_key:
            try:
                self.translator = deepl.Translator(self.auth_key)
                logging.info("DeepL API Initialized.")
            except Exception as e:
                logging.error(f"DeepL Init Failed: {e}")
        else:
            logging.warning("DEEPL_AUTH_KEY not found. Running in Mock Mode.")

        # 2. Initialize RAG (ChromaDB)
        logging.info("Initializing RAG Engine...")
        self.chroma_client = chromadb.PersistentClient(path=db_path)
        self.emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        self.collection = self.chroma_client.get_or_create_collection(
            name="translation_memory",
            embedding_function=self.emb_fn
        )
        
        # 3. Load Data
        self.glossary_map = self._load_glossary()
        self._index_corpus()
        
        # 4. Create/Get DeepL Glossary ID
        self.deepl_glossary = None
        if self.translator and self.glossary_map:
            self.deepl_glossary = self._sync_deepl_glossary()

    def _load_glossary(self) -> Dict[str, str]:
        if os.path.exists(self.glossary_path):
            with open(self.glossary_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Filter empty values
                return {k: v for k, v in data.items() if v}
        return {}

    def _index_corpus(self):
        """Read corpus file and index into ChromaDB if not already indexed."""
        # Check if DB is empty to avoid re-indexing every run (Simple optimization)
        if self.collection.count() > 0:
            logging.info(f"RAG DB already contains {self.collection.count()} items.")
            return

        if not os.path.exists(self.corpus_path):
            logging.warning(f"Corpus file missing: {self.corpus_path}")
            return

        documents = []
        metadatas = []
        ids = []
        
        with open(self.corpus_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if "->" not in line: continue
                src, tgt = line.split("->", 1)
                documents.append(src.strip())
                metadatas.append({"translation": tgt.strip()})
                ids.append(f"doc_{i}")
        
        if documents:
            self.collection.add(documents=documents, metadatas=metadatas, ids=ids)
            logging.info(f"Indexed {len(documents)} pairs to RAG DB.")

    def _sync_deepl_glossary(self):
        """Uploads local glossary to DeepL and returns the GlossaryInfo object."""
        try:
            entries = self.glossary_map
            if not entries: return None
            
            logging.info(f"Syncing Glossary to DeepL ({len(entries)} terms)...")
            # Create a new glossary (Note: DeepL allows duplicates, ideally we manage IDs)
            # For this script, we create a fresh one named 'Moim_Glossary'
            return self.translator.create_glossary(
                "Moim_Glossary",
                source_lang="KO",
                target_lang="EN",
                entries=entries
            )
        except Exception as e:
            logging.error(f"Failed to sync glossary: {e}")
            return None

    def construct_rag_prompt(self, text: str, similar_docs: list) -> str:
        """
        Constructs a prompt with RAG context. 
        Useful if we switch to LLM or for debugging/logging context utility.
        """
        prompt = "You are a translator for a University Christian Community.\n"
        prompt += "Use the following context to understand specific terms:\n"
        
        if similar_docs:
            prompt += "--- Reference Context ---\n"
            for doc, meta in zip(similar_docs['documents'][0], similar_docs['metadatas'][0]):
                prompt += f"Source: {doc}\nReference: {meta['translation']}\n"
            prompt += "-------------------------\n"
            
        prompt += f"Input Text: {text}\n"
        return prompt

    def translate(self, text: str):
        # 1. RAG Retrieval
        results = self.collection.query(query_texts=[text], n_results=1)
        
        # 2. Design Prompt (As requested by user)
        rag_prompt = self.construct_rag_prompt(text, results)
        logging.info(f"[Designed Prompt]\n{rag_prompt}")
        
        # 3. Translation Execution
        try:
            if self.translator and self.deepl_glossary:
                # Use DeepL with Glossary
                res = self.translator.translate_text(
                    text, 
                    target_lang="EN-US", 
                    glossary=self.deepl_glossary
                )
                return res.text
            elif self.translator:
                # DeepL without Glossary
                res = self.translator.translate_text(text, target_lang="EN-US")
                return res.text
            else:
                # Mock Mode: Simple replacement using local glossary
                translated = text
                for k, v in self.glossary_map.items():
                    translated = translated.replace(k, f"[{v}]")
                return f"[Mock DeepL] {translated}"
                
        except Exception as e:
            logging.error(f"Translation Error: {e}")
            return f"[Error] {text}"

def main():
    base_dir = Path(__file__).parent.parent
    glossary_path = base_dir / "references" / "glossary.json"
    corpus_path = base_dir / "references" / "ebc_corpus.txt"
    
    engine = TranslatorEngine(str(glossary_path), str(corpus_path))
    
    # Test Case
    input_text = "이번주 작업지원을 나가서 지체들과 교제를 나눴습니다."
    print(f"\nOriginal: {input_text}")
    print("-" * 30)
    
    translation = engine.translate(input_text)
    print("-" * 30)
    print(f"Result: {translation}")

if __name__ == "__main__":
    main()
