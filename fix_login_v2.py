import os

target_file = "backend/streamlit_app.py"

# 1. 로그인 검증 강화 + 2. 안전한 테이블 생성 코드
final_code = """import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class EbcCrawler:
    def __init__(self):
        self.session = requests.Session()
        # 모바일 브라우저 위장
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
            'Referer': 'https://m.ebcblue.com/',
            'Origin': 'https://m.ebcblue.com'
        }
        self.login_url = "https://m.ebcblue.com/bbs/login_check.php"

    def login(self, user_id, user_pw):
        try:
            # 1. 로그인 요청
            data = {'mb_id': user_id, 'mb_password': user_pw, 'url': 'https://m.ebcblue.com/'}
            self.session.post(self.login_url, data=data, headers=self.headers, verify=False)
            
            # 2. 메인 페이지에서 '로그아웃' 버튼 확인 (검증)
            res = self.session.get('https://m.ebcblue.com/', headers=self.headers, verify=False)
            res.encoding = res.apparent_encoding
            
            if '로그아웃' in res.text or 'logout' in res.text:
                return True
            else:
                return False
        except: return False

    def scan_links(self, url, keyword):
        st.info("🔍 페이지 스캔 중...")
        found_data = []
        
        try:
            res = self.session.get(url, headers=self.headers, verify=False)
            res.encoding = res.apparent_encoding
            soup = BeautifulSoup(res.text, 'html.parser')

            # 키워드 검사
            if keyword and keyword not in res.text:
                st.error(f"❌ 페이지 내에 '{keyword}'라는 텍스트가 없습니다.")
                st.warning("로그인이 안 됐거나 권한이 없는 페이지일 수 있습니다.")
                return []

            # 링크 수집
            for a in soup.find_all('a', href=True):
                text = a.get_text(strip=True)
                href = a['href']
                full_link = urljoin(url, href)

                if not keyword or (keyword and keyword in text):
                    if len(text) > 0 and 'javascript' not in href:
                        found_data.append({
                            "제목": text,
                            "링크": full_link
                        })
            return found_data

        except Exception as e:
            st.error(f"에러: {e}")
            return []

# UI 구성
st.set_page_config(page_title="MOIM 번역기 (Final)", layout="wide")
st.title("🔐 MOIM 번역기 : 회원 전용 모드")

with st.sidebar:
    st.header("로그인")
    user_id = st.text_input("아이디", key="uid")
    user_pw = st.text_input("비밀번호", type="password", key="upw")

st.subheader("1. 검색 설정")
url = st.text_input("타겟 URL", "http://m.ebcblue.com/")
keyword = st.text_input("찾을 키워드 (예: 실습)", placeholder="비워두면 모든 글을 봅니다")

if st.button("🚀 로그인하고 검색 시작"):
    if not user_id or not user_pw:
        st.error("아이디와 비밀번호를 입력해주세요.")
    else:
        crawler = EbcCrawler()
        status = st.empty()
        status.info("🔑 로그인 검증 중...")
        
        if crawler.login(user_id, user_pw):
            status.success("✅ 로그인 성공! (로그아웃 버튼 확인됨)")
            
            results = crawler.scan_links(url, keyword)
            
            if results:
                st.success(f"🎉 '{keyword}' 관련 항목 {len(results)}개를 찾았습니다!")
                st.write("### 📋 검색 결과")
                
                # [수정됨] 에러 방지를 위해 줄을 짧게 나눴습니다
                table_head = "| 제목 | 바로가기 |\\n"
                table_div = "|---|---|\\n"
                md_table = table_head + table_div
                
                for row in results:
                    # 링크 포맷팅
                    link_text = f"[이동하기]({row['링크']})"
                    row_str = f"| {row['제목']} | {link_text} |\\n"
                    md_table += row_str
                
                st.markdown(md_table)
            else:
                st.warning("결과가 없습니다.")
        else:
            status.error("❌ 로그인 실패!")
            st.caption("서버가 로그인을 거부했습니다. 아이디/비번을 다시 확인해주세요.")
"""

with open(target_file, "w", encoding="utf-8") as f:
    f.write(final_code)

print("✅ [수정 완료] 문법 오류를 해결했습니다.")
