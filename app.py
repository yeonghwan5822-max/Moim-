import streamlit as st
import traceback
import os
import sys
import pandas as pd
import time
from pathlib import Path

# [Step 1] Page Config (Must be the very first command)
st.set_page_config(page_title="MOIM Smart Workstation", layout="wide", page_icon="🏫")

# [Deployment Fix] Workaround for ChromaDB requiring sqlite3 >= 3.35
try:
    __import__('pysqlite3')
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass # Locally or if missing, might fail later but let's try

try:
    # [Step 2] Absolute Path Setup
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    if BASE_DIR not in sys.path:
        sys.path.append(BASE_DIR)

    # [Step 3] Import Backend Modules
    from backend.scripts.crawler import EbcCrawler
    from backend.scripts.translator_engine import TranslatorEngine
    from backend.scripts.pure_collector import PureCollector

    # [Step 4] Initialize Resources
    @st.cache_resource
    def get_translator():
        glossary_path = os.path.join(BASE_DIR, "backend", "references", "glossary.json")
        corpus_path = os.path.join(BASE_DIR, "backend", "references", "ebc_corpus.txt")
        return TranslatorEngine(glossary_path, corpus_path)

    try:
        translator = get_translator()
    except Exception as e:
        st.warning(f"⚠️ Translator partially initialized: {e}")
        translator = None

    # [Step 5] Custom UI Styling
    st.markdown("""
    <style>
        .stApp { background-color: #f2f4f6; }
        .main-container { background-color: white; padding: 2rem; border-radius: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
        h1 { font-family: 'Suit', sans-serif; color: #191f28; }
        .stTabs [data-baseweb="tab-list"] { gap: 20px; }
        .stTabs [data-baseweb="tab"] { height: 50px; background-color: white; border-radius: 10px; padding: 10px 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
        .stTabs [aria-selected="true"] { background-color: #3182F6; color: white; }
    </style>
    """, unsafe_allow_html=True)

    st.title("🏫 MOIM Smart Workstation")

    # [Step 6] Tabs & Main Logic
    tab1, tab2 = st.tabs(["🤖 번역기 (Translator)", "🕷️ 데이터 수집 (Data Collector)"])

    # --- TAB 1: Translator ---
    with tab1:
        with st.container():
            st.markdown("### ⚙️ 설정 (Settings)")
            col1, col2 = st.columns([1, 1])
            with col1:
                target_lang_map = {
                    "영어 (English)": "EN-US", "일본어 (Japanese)": "JA", "중국어 (Chinese)": "ZH",
                    "베트남어 (Vietnamese)": "VI", "스페인어 (Spanish)": "ES", "프랑스어 (French)": "FR"
                }
                selected_label = st.selectbox("도착 언어", options=list(target_lang_map.keys()), index=0, key="tab1_lang")
                target_lang_code = target_lang_map[selected_label]
            with col2:
                phpsessid = st.text_input("PHPSESSID (로그인 세션)", type="password", key="tab1_sessid")

        st.divider()
        url_input = st.text_input("🔗 번역할 게시글/게시판 URL", key="tab1_url")
        keyword = st.text_input("🔍 (선택) 검색어 필터", key="tab1_kw")

        if st.button("🚀 번역 시작", type="primary", key="tab1_btn"):
            if not phpsessid:
                st.warning("⚠️ PHPSESSID 필요")
            elif not url_input:
                st.warning("⚠️ URL 필요")
            else:
                with st.spinner("데이터 처리 중..."):
                    crawler = EbcCrawler()
                    crawler.session.cookies.set("PHPSESSID", phpsessid, domain="m.ebcblue.com")
                    if 'wr_id=' in url_input:
                        links = [url_input]
                    else:
                        res = crawler.get_categorized_links(url_input, keyword)
                        links = res.get('normal', []) + res.get('notice', [])
                
                if not links:
                    st.error("게시글을 찾을 수 없습니다.")
                else:
                    progress_bar = st.progress(0)
                    for idx, link in enumerate(links):
                        data = crawler.get_post_content(link)
                        if data['title'] == "Error" or not data['content']: continue
                        
                        trans_title = translator.translate(data['title'], target_lang=target_lang_code) if translator else data['title']
                        trans_content = translator.translate(data['content'][:3000], target_lang=target_lang_code) if translator else data['content']
                        
                        with st.expander(f"📄 {trans_title}", expanded=(idx==0)):
                            c1, c2 = st.columns(2)
                            c1.text(data['content'])
                            c2.markdown(trans_content)
                            st.caption(f"Source: {link}")
                        progress_bar.progress((idx+1)/len(links))

    # --- TAB 2: Data Collector ---
    with tab2:
        st.markdown("### 🕷️ Raw Data Collector")
        st.write("학습용 데이터셋 수집 도구")
        
        collect_url = st.text_input("게시판 URL", value="https://m.ebcblue.com/bbs/board.php?bo_table=free", key="tab2_url")
        c1, c2 = st.columns(2)
        collect_sessid = c1.text_input("PHPSESSID", type="password", key="tab2_sessid")
        collect_pages = c2.number_input("페이지 수", min_value=1, value=1, key="tab2_pages")
        
        if st.button("🚀 데이터 수집 시작", type="primary", key="tab2_btn"):
            if not collect_sessid:
                st.error("PHPSESSID 필요")
            else:
                collector = PureCollector(collect_sessid)
                status = st.status("수집 시작...", expanded=True)
                links = collector.get_board_links(collect_url, collect_pages)
                
                if not links:
                    status.update(label="실패: 게시글 없음", state="error")
                else:
                    status.write(f"{len(links)}개 게시글 발견")
                    prog = st.progress(0)
                    for i, link in enumerate(links):
                        collector.process_post(link)
                        prog.progress((i+1)/len(links))
                        time.sleep(0.1)
                    
                    status.update(label="완료!", state="complete")
                    if collector.raw_data:
                        df = pd.DataFrame(collector.raw_data)
                        csv = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
                        st.download_button("📥 CSV 다운로드", csv, "moim_raw_data.csv", "text/csv")

except Exception as e:
    # [EMERGENCY MODE] Display Error Traceback on UI
    st.error("🚨 앱 실행 중 치명적인 오류가 발생했습니다!")
    st.markdown("### 아래 오류 내용을 캡처해서 개발자에게 전달주세요.")
    st.code(traceback.format_exc())
