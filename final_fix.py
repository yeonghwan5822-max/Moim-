import os

# 1. 로그인 기능이 있는 새 화면 코드 (backend/streamlit_app.py)
app_code = """import streamlit as st
import sys
import os

# 경로 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from scripts.crawler import EbcCrawler

st.set_page_config(page_title="MOIM 번역기 (Member Only)", layout="wide")

st.title("🔐 MOIM 번역기 : 회원 전용 모드")

# [사이드바] 로그인 정보 입력
with st.sidebar:
    st.header("1. 로그인 정보")
    st.info("🔒 게시글을 보려면 로그인이 필수입니다.")
    user_id = st.text_input("아이디 (ID)", placeholder="사이트 아이디 입력")
    user_pw = st.text_input("비밀번호 (PW)", type="password")

st.header("2. 크롤링 설정")
url = st.text_input("타겟 URL", "http://m.ebcblue.com/")
keyword = st.text_input("키워드 (선택사항)", placeholder="비워두면 모든 글을 가져옵니다")

if st.button("🚀 로그인하고 게시물 찾기"):
    if not user_id or not user_pw:
        st.error("❌ 왼쪽 사이드바에 아이디와 비밀번호를 먼저 입력해주세요!")
    else:
        crawler = EbcCrawler()
        status_box = st.empty()
        status_box.info("🔑 로그인 시도 중...")
        
        # 1. 로그인 시도
        if crawler.login(user_id, user_pw):
            status_box.success(f"✅ '{user_id}'님 로그인 성공! 데이터 수집을 시작합니다.")
            
            # 2. 크롤링 시작
            results = crawler.get_categorized_links(url, keyword)
            links = results.get('normal', [])
            
            st.divider()
            if links:
                st.success(f"🎉 총 {len(links)}개의 게시물을 찾았습니다!")
                st.write("### 📄 발견된 게시물 목록")
                for link in links:
                    st.write(f"- {link}")
            else:
                st.warning("로그인은 성공했으나, 게시물을 찾지 못했습니다.")
        else:
            status_box.error("❌ 로그인 실패! 아이디와 비밀번호를 확인해주세요.")
"""

# 2. 라이브러리 목록 다이어트 (backend/requirements.txt)
req_code = """streamlit==1.31.0
requests
beautifulsoup4
urllib3
"""

# 파일 덮어쓰기 (경로 강제 지정)
with open("backend/streamlit_app.py", "w", encoding="utf-8") as f:
    f.write(app_code)

with open("backend/requirements.txt", "w", encoding="utf-8") as f:
    f.write(req_code)

print("✅ [성공] 옛날 코드를 삭제하고 '로그인 버전'으로 교체했습니다!")
