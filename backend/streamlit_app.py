
import streamlit as st
import sys
import os
from pathlib import Path

# Add backend to sys.path to resolve imports
current_dir = Path(__file__).parent
backend_dir = current_dir.parent
sys.path.append(str(backend_dir))

from backend.scripts.crawler import EbcCrawler
from backend.scripts.translator_engine import TranslatorEngine

# UI Configuration
st.set_page_config(page_title="MOIM Smart Translator", layout="wide", page_icon="🌍")

# Initialize Translator Engine (Singleton-like)
@st.cache_resource
def get_translator():
    # Paths relative to backend/
    base_dir = current_dir.parent
    glossary_path = base_dir / "backend/references/glossary.json"
    corpus_path = base_dir / "backend/references/ebc_corpus.txt"
    return TranslatorEngine(str(glossary_path), str(corpus_path))

try:
    translator = get_translator()
except Exception as e:
    st.error(f"Translator Initialization Failed: {e}")
    translator = None

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
</style>
""", unsafe_allow_html=True)

st.title("🌍 MOIM 번역기 : Global Mode")

# --- Sidebar / Header Controls ---
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
            index=0
        )
        target_lang_code = target_lang_map[selected_label]
        
    with col2:
        phpsessid = st.text_input(
            "PHPSESSID (로그인 세션)", 
            placeholder="마이페이지 > 쿠키에서 복사 붙여넣기", 
            type="password"
        )

st.divider()

# --- Main Input ---
url_input = st.text_input("🔗 번역할 게시글/게시판 URL", placeholder="https://m.ebcblue.com/bbs/board.php?bo_table=...")
keyword = st.text_input("🔍 (선택) 검색어 필터", placeholder="예: 실습, 공지")

if st.button("🚀 번역 시작 (Translate)", type="primary"):
    if not phpsessid:
        st.warning("⚠️ PHPSESSID를 입력해주세요 (로그인 필수).")
    elif not url_input:
        st.warning("⚠️ URL을 입력해주세요.")
    else:
        with st.spinner("🕵️‍♂️ 사이트에 접속하여 데이터를 수집하고 있습니다..."):
            crawler = EbcCrawler()
            crawler.session.cookies.set("PHPSESSID", phpsessid, domain="m.ebcblue.com")
            
            # 1. Links Collection
            # Uses existing crawler logic which returns dict {'notice': [], 'normal': []}
            if 'wr_id=' in url_input:
                # Direct post access
                links = [url_input]
            else:
                # List scan
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
                # We translate Title and Content
                with st.spinner(f"번역 중... {post_data['title'][:10]}..."):
                    translated_title = translator.translate(post_data['title'], target_lang=target_lang_code)
                    
                    # Split content for better translation (simple chunking by newline for now if too long)
                    # For V1, pass full content if < 2000 chars, else just translate the first chunk or summary
                    # DeepL has limits, be careful.
                    content_to_translate = post_data['content'][:3000] # Limit char count for PoC
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
