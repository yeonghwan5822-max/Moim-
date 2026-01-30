import streamlit as st
import sys
import os
import json
import logging
from pathlib import Path
import time
import random
import pandas as pd

# Add backend root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import Skills
from scripts.crawler import EbcCrawler
from scripts.translator_engine import TranslatorEngine
from skills.analyzer.model import OOVAnalyzer
from scripts.oov_detector import KNOWN_BIBLICAL_TERMS, COMMON_STOPWORDS, clean_word, load_text_file

def convert_to_excel(json_data):
    """
    Convert JSON to Excel with strictly defined columns.
    """
    from io import BytesIO
    output = BytesIO()
    
    rows = []
    
    for idx, item in enumerate(json_data):
        rows.append({
            "게시글ID": idx + 1,
            "주제": item.get('category', '기타'),
            "제목": item.get('title', ''),
            "본문내용": item.get('content', ''),
            "링크": item.get('url', '')
        })
        
    df = pd.DataFrame(rows)
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Corpus_Data')
        
    return output.getvalue()

# Setup Page
st.set_page_config(page_title="Moim Translator Demo", layout="wide")
st.title("✝️ Moim Translator - Integrated PoC Demo")

# Tabs
tab1, tab2, tab3 = st.tabs(["🕷️ Crawler", "📊 OOV Detector", "🌏 Translator (RAG)"])

# --- TAB 1: CRAWLER ---
with tab1:
    st.header("Community Crawler & Corpora Builder")
    st.info("Fetches posts and merges them into the corpus for RAG/OOV analysis.")
    
    # 1. Mode Selection
    crawl_mode = st.radio("Select Crawl Mode", ["📋 Board Auto-Discovery (Bulk)", "🔗 Single Page (Test)"], horizontal=True)
    
    col1, col2 = st.columns([2, 1])
    
    # 2. Dynamic Inputs based on Mode
    if crawl_mode == "📋 Board Auto-Discovery (Bulk)":
        with col1:
            target_url = st.text_input("Board URL", value="http://m.ebcblue.com/bbs/board.php?bo_table=practice")
        with col2:
            keyword = st.text_input("Keywords (Optional)", value="실습")
        max_pages = st.slider("Pages to Scan", 1, 5, 2)
    else:
        with col1:
            target_url = st.text_input("Post URL", value="http://m.ebcblue.com/bbs/board.php?bo_table=practice&wr_id=123")
        with col2:
            keyword = None # Not used
        max_pages = 1
    
    use_simulation = st.checkbox("✅ Simulation Mode (Recommend for Demo)", value=True)

    # Initialize Session State
    if "collected_links" not in st.session_state:
        st.session_state.collected_links = []
    if "cat_metadata" not in st.session_state:
        st.session_state.cat_metadata = {}

    # Buttons layout
    btn_col1, btn_col2 = st.columns([1, 1])

    with btn_col1:
        if st.button("🔍 1. Find Posts (List Only)"):
            st.session_state.collected_links = [] # Reset
            st.session_state.cat_metadata = {}
            
            crawler = EbcCrawler(headless=True)
            try:
                with st.spinner(f"Scanning..."):
                    if "Single" in crawl_mode:
                         # Single Page Mode: Direct Add
                         links = [{"title": "Single Target", "url": target_url}]
                         cat_result = {"category": "Single Page", "found_links": links}
                         # Validate? Optional.
                         time.sleep(0.5) 
                    
                    elif use_simulation:
                        # Mock Logic
                        time.sleep(1)
                        links = [{"title": f"Mock Post {i}", "url": f"http://mock.site/{i}"} for i in range(5)]
                        cat_result = {"category": keyword or "All", "found_links": links}
                    else:
                        # Real Logic (Bulk)
                        cat_result = crawler.get_categorized_links(target_url, keyword, max_pages)
                
                st.session_state.collected_links = cat_result.get("found_links", [])
                st.session_state.cat_metadata = cat_result
                
                if not st.session_state.collected_links:
                     st.warning("No links found.")
                else:
                    st.success(f"✅ Found {len(st.session_state.collected_links)} posts!")

            except Exception as e:
                st.error(f"Search failed: {e}")
            finally:
                crawler.close()

    # Display Table if data exists
    if st.session_state.collected_links:
        st.divider()
        st.subheader(f"📑 Found Posts: {len(st.session_state.collected_links)} items")
        
        # Display as DataFrame with Clickable Links
        df_links = pd.DataFrame(st.session_state.collected_links)
        st.dataframe(
            df_links,
            column_config={
                "url": st.column_config.LinkColumn("Post URL")
            },
            use_container_width=True
        )
        
        # Step 2: Extraction
        with btn_col2:
            if st.button("📥 2. Extract Content from List"):
                STATUS = st.empty()
                PBAR = st.progress(0)
                collected_data = []
                
                links = st.session_state.collected_links
                category = st.session_state.cat_metadata.get("category", "Uncategorized")
                
                crawler = EbcCrawler(headless=True)
                try:
                    STATUS.info("Starting Batch Extraction...")
                    total = len(links)
                    
                    for i, link in enumerate(links):
                        STATUS.write(f"Extracting ({i+1}/{total}): {link['title']}")
                        
                        if use_simulation:
                            time.sleep(0.5)
                            detail = {"status": "success", "title": link['title'], "url": link['url'], "content": f"Simulated content for {link['title']}", "category": category}
                        else:
                            detail = crawler.crawl_detail(link['url'], link['title'])
                            detail['category'] = category
                        
                        if detail.get("status") == "success":
                            collected_data.append(detail)
                        else:
                            logging.warning(f"Skipping {link['url']}: {detail.get('reason')}")
                        
                        PBAR.progress(int((i+1)/total * 100))
                        time.sleep(random.uniform(1.0, 3.0))
                        
                    # Finalize
                    STATUS.success("Extraction Complete!")
                    st.json(collected_data)
                    
                    # Save Logic
                    json_path = Path("data/raw/streamlit_crawl.json")
                    json_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(json_path, "w", encoding="utf-8") as f:
                        json.dump(collected_data, f, ensure_ascii=False, indent=2)
                        
                    # Corpus Merge
                    corpus_path = Path("references/ebc_corpus.txt")
                    with open(corpus_path, "a", encoding="utf-8") as f:
                        for item in collected_data:
                            clean_content = item['content'].replace("\n", " ")
                            if len(clean_content) > 10:
                                f.write(f"\n{clean_content}")
                    
                    st.toast(f"Saved {len(collected_data)} items to corpus.", icon="💾")
                    
                except Exception as e:
                    st.error(f"Extraction Error: {e}")
                finally:
                    crawler.close()
            


# --- TAB 2: OOV DETECTOR ---
with tab2:
    st.header("OOV (Out-of-Vocabulary) Detector")
    st.info("Analyzes text to find community-specific slang/terms.")
    
    input_source = st.radio("Input Source", ["Sample Corpus", "Crawled Data"])
    
    corpus_text = []
    if input_source == "Sample Corpus":
        corpus_path = Path("references/corpus_sample.txt")
        if corpus_path.exists():
            with open(corpus_path, "r", encoding="utf-8") as f:
                corpus_text = [line.strip() for line in f if line.strip()]
            st.text_area("Sample Text Preview", value="\n".join(corpus_text[:5]) + "\n...", height=100)
    else:
        crawl_path = Path("data/raw/streamlit_crawl.json")
        if crawl_path.exists():
            with open(crawl_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                corpus_text = [item['content'] for item in data]
            st.text_area("Crawled Text Preview", value="\n".join(corpus_text[:2]) + "\n...", height=100)
        else:
            st.warning("No crawled data found. Please run Crawler first.")

    if st.button("Run OOV Analysis"):
        if not corpus_text:
            st.error("No text to analyze.")
        else:
            with st.spinner("Training soynlp model..."):
                # Hack: Repeat small corpus
                train_corpus = corpus_text * 20 if len(corpus_text) < 100 else corpus_text
                
                analyzer = OOVAnalyzer()
                analyzer.train(train_corpus)
                candidates = analyzer.get_top_scored_words(top_k=50)
                
                # Filter Logic
                results = []
                for cand in candidates:
                    word = clean_word(cand['word'])
                    if len(word) < 2: continue
                    
                    status = "New Candidate"
                    if word in KNOWN_BIBLICAL_TERMS: status = "Biblical (Skip)"
                    elif word in COMMON_STOPWORDS: status = "Stopword (Skip)"
                    
                    results.append({
                        "Word": word,
                        "Score": cand['combined_score'],
                        "Status": status,
                        "Type": "OOV"
                    })

                # --- NEW: Contextual Anomaly ---
                from scripts.oov_detector import ContextualDetector
                ctx_detector = ContextualDetector()
                anomalies = ctx_detector.detect_anomalies(train_corpus)
                
                for ano in anomalies:
                    results.append({
                        "Word": ano['word'],
                        "Score": 99.9, # Max score for context
                        "Status": f"Context Warning ({len(ano['pairs'])} pairs)",
                        "Type": "Context"
                    })
                
                df = pd.DataFrame(results)
                st.dataframe(df, use_container_width=True)
                
                # Highlight New Terms
                new_terms = df[df['Status'] == "New Candidate"]['Word'].tolist()
                if new_terms:
                    st.success(f"Found {len(new_terms)} potential new terms: {', '.join(new_terms[:5])}...")

    # --- TAB 1 (Merged Logic): Excel Export Button ---
    # We place this here because it uses 'collected_data' from Tab 1 or OOV context
    st.divider()
    st.header("📥 Export Data")
    
    crawl_path = Path("data/raw/streamlit_crawl.json")
    if crawl_path.exists():
        with open(crawl_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        if st.download_button(
            label="Download Excel Report (community_corpus.xlsx)",
            data=convert_to_excel(data),
            file_name="community_corpus.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ):
            st.toast("Download Started!", icon="📥")
    else:
        st.caption("No data available to export.")




# --- TAB 3: TRANSLATOR ---
with tab3:
    st.header("RAG-Enhanced Translator")
    st.info("Translates text using DeepL + Community Glossary + RAG Context.")
    
    user_input = st.text_area("Enter text to translate", 
                              value="이번주 작업지원을 나가서 지체들과 교제를 나눴습니다.")
    
    if st.button("Translate"):
        glossary_path = Path("references/glossary.json")
        corpus_path = Path("references/ebc_corpus.txt")
        
        with st.spinner("Retrieving context and translating..."):
            engine = TranslatorEngine(str(glossary_path), str(corpus_path))
            
            # 1. RAG Context
            context_results = engine.collection.query(query_texts=[user_input], n_results=1)
            
            col_res1, col_res2 = st.columns(2)
            
            with col_res1:
                st.subheader("RAG Context Retrieval")
                if context_results['documents'] and context_results['documents'][0]:
                    sim_doc = context_results['documents'][0][0]
                    sim_trans = context_results['metadatas'][0][0]['translation']
                    st.markdown(f"**Similar Source:** `{sim_doc}`")
                    st.markdown(f"**Reference:** `{sim_trans}`")
                else:
                    st.info("No similar context found.")

            with col_res2:
                st.subheader("Translation Result")
                final_trans = engine.translate(user_input)
                st.success(final_trans)
                
            # Glossary Debug
            st.expander("Active Glossary Terms").json(engine.glossary_map)
