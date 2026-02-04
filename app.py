
import streamlit as st
import sys
import os
import pandas as pd
import time
# [Fix] Workaround for ChromaDB requiring sqlite3 >= 3.35
__import__('pysqlite3')
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

# -------------------------------------------------------------
# [Deployment Fix] Absolute Path Strategy
# -------------------------------------------------------------
# Get the absolute path of the current file (app.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Add BASE_DIR to sys.path to ensure we can import 'backend'
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# Import strictly from backend package
from backend.scripts.crawler import EbcCrawler
from backend.scripts.translator_engine import TranslatorEngine
from backend.scripts.pure_collector import PureCollector

# UI Configuration
st.set_page_config(page_title="MOIM Smart Workstation", layout="wide", page_icon="🏫")

# Initialize Translator Engine (Singleton-like)
@st.cache_resource
def get_translator():
    # Use robust absolute paths
    glossary_path = os.path.join(BASE_DIR, "backend", "references", "glossary.json")
    corpus_path = os.path.join(BASE_DIR, "backend", "references", "ebc_corpus.txt")
    
    # Debug information for deployment logs
    print(f"[Info] Base Dir: {BASE_DIR}")
    print(f"[Info] Glossary Path: {glossary_path}")
    print(f"[Info] Corpus Path: {corpus_path}")
    
    # Check if files exist to avoid crash loop
    if not os.path.exists(glossary_path):
        print(f"[Error] Glossary NOT found at {glossary_path}")
    if not os.path.exists(corpus_path):
        print(f"[Error] Corpus NOT found at {corpus_path}")
        
    return TranslatorEngine(glossary_path, corpus_path)

# Custom CSS for "Toss" style
st.markdown("""
<style>
    .stApp {
        background-color: #f2f4f6;
    }
    div[data-testid="stToolbar"] {
        visibility: hidden;
    }
    .main-container {
        background-color: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
    h1 {
        font-family: 'Suit', sans-serif;
        color: #191f28;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: white;
        border-radius: 10px;
        padding: 10px 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .stTabs [aria-selected="true"] {
        background-color: #3182F6;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

st.title("🏫 MOIM Smart Workstation")

# Create Tabs
tab1, tab2 = st.tabs(["🤖 번역기 (Translator)", "🕷️ 데이터 수집 (Data Collector)"])

# ==========================================
# TAB 1: 번역기 (Translator)
# ==========================================
with tab1:
    with st.container():
        st.markdown("### ⚙️ 설정 (Settings)")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Language Selector
            target_lang_map = {
                "영어 (English)": "EN-US",
                "일본어 (Japanese)": "JA",
                "중국어 (Chinese)": "ZH",
                "베트남어 (Vietnamese)": "VI",
                "스페인어 (Spanish)": "ES",
                "프랑스어 (French)": "FR"
            }
            selected_label = st.selectbox(
                "도착 언어 (Target Language)",
                options=list(target_lang_map.keys()),
                index=0,
                key="tab1_lang"
            )
            target_lang_code = target_lang_map[selected_label]
            
        with col2:
            phpsessid = st.text_input(
                "PHPSESSID (로그인 세션)", 
                placeholder="마이페이지 > 쿠키에서 복사 붙여넣기", 
                type="password",
                key="tab1_sessid"
            )

    st.divider()

    # --- Main Input ---
    url_input = st.text_input("🔗 번역할 게시글/게시판 URL", placeholder="https://m.ebcblue.com/bbs/board.php?bo_table=...", key="tab1_url")
    keyword = st.text_input("🔍 (선택) 검색어 필터", placeholder="예: 실습, 공지", key="tab1_kw")

    if st.button("🚀 번역 시작 (Translate)", type="primary", key="tab1_btn"):
        if not phpsessid:
            st.warning("⚠️ PHPSESSID를 입력해주세요 (로그인 필수).")
        elif not url_input:
            st.warning("⚠️ URL을 입력해주세요.")
        else:
            with st.spinner("🕵️‍♂️ 사이트에 접속하여 데이터를 수집하고 있습니다..."):
                crawler = EbcCrawler()
                crawler.session.cookies.set("PHPSESSID", phpsessid, domain="m.ebcblue.com")
                
                # 1. Links Collection
                if 'wr_id=' in url_input:
                    links = [url_input]
                else:
                    crawl_result = crawler.get_categorized_links(url_input, keyword)
                    links = crawl_result.get('normal', []) + crawl_result.get('notice', [])

            if not links:
                st.error("게시글을 찾을 수 없습니다. 로그인 세션이 만료되었거나 권한이 없을 수 있습니다.")
            else:
                st.success(f"총 {len(links)}개의 게시글을 발견했습니다. 번역을 시작합니다!")
                
                progress_bar = st.progress(0)
                
                for idx, link in enumerate(links):
                    # 2. Extract Content
                    post_data = crawler.get_post_content(link)
                    
                    if post_data['title'] == "Error" or not post_data['content']:
                        continue
                        
                    # 3. Translate
                    with st.spinner(f"번역 중... {post_data['title'][:10]}..."):
                        translated_title = translator.translate(post_data['title'], target_lang=target_lang_code)
                        content_to_translate = post_data['content'][:3000] # Limit
                        translated_content = translator.translate(content_to_translate, target_lang=target_lang_code)

                    # 4. Display Result
                    with st.expander(f"📄 {translated_title} (Original: {post_data['title']})", expanded=(idx==0)):
                        c1, c2 = st.columns(2)
                        with c1:
                            st.markdown("**[Original]**")
                            st.text(post_data['content'])
                        with c2:
                            st.markdown(f"**[{selected_label}]**")
                            st.markdown(translated_content)
                            
                        st.caption(f"Source: {link}")
                    
                    progress_bar.progress((idx + 1) / len(links))

# ==========================================
# TAB 2: 데이터 수집 (Data Collector)
# ==========================================
with tab2:
    st.markdown("### 🕷️ Raw Data Collector")
    st.caption("번역 없이 순수 한국어 텍스트 데이터를 수집하여 학습용 데이터셋을 구축합니다.")
    
    with st.container():
        st.markdown("#### 구역 설정 (Target Zone)")
        collect_url = st.text_input(
            "게시판 URL", 
            value="https://m.ebcblue.com/bbs/board.php?bo_table=free",
            key="tab2_url"
        )
        
        c1, c2 = st.columns(2)
        with c1:
            collect_sessid = st.text_input(
                "로그인 키 (PHPSESSID)", 
                type="password",
                key="tab2_sessid"
            )
        with c2:
            collect_pages = st.number_input(
                "수집할 페이지 수 (Pages)", 
                min_value=1, max_value=10, value=1,
                key="tab2_pages"
            )
            
    st.divider()
    
    if st.button("🚀 데이터 수집 시작", type="primary", key="tab2_btn"):
        if not collect_sessid:
            st.error("🔒 로그인을 위해 PHPSESSID가 필요합니다.")
        else:
            collector = PureCollector(collect_sessid)
            status_container = st.status("🕵️‍♂️ 데이터 수집을 시작합니다...", expanded=True)
            
            try:
                # 1. Link Collection
                status_container.write(f"📡 게시판({collect_url})을 스캔하고 있습니다...")
                target_links = collector.get_board_links(collect_url, collect_pages)
                
                if not target_links:
                    status_container.update(label="❌ 수집 실패: 게시글을 찾지 못했습니다.", state="error")
                else:
                    status_container.write(f"✅ 총 {len(target_links)}개의 게시글을 발견했습니다. 상세 수집을 시작합니다.")
                    
                    # 2. Detail Collection
                    prog_bar = st.progress(0)
                    for i, link in enumerate(target_links):
                        collector.process_post(link)
                        prog_bar.progress((i + 1) / len(target_links))
                        time.sleep(0.1)
                    
                    status_container.update(label="✨ 수집 완료! 데이터를 변환 중입니다...", state="complete")
                    
                    # 3. CSV Conversion
                    if collector.raw_data:
                        df = pd.DataFrame(collector.raw_data)
                        csv = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
                        
                        st.success(f"🎉 작업 완료! 총 {len(df)}개의 데이터 청크가 수집되었습니다.")
                        st.download_button(
                            label="📥 moim_raw_data.csv 다운로드",
                            data=csv,
                            file_name="moim_raw_data.csv",
                            mime="text/csv",
                        )
                    else:
                        st.warning("수집된 데이터가 없습니다.")
                        
            except Exception as e:
                status_container.update(label="⚠️ 오류 발생", state="error")
                st.error(f"Error: {e}")
