import os

target_file = "backend/streamlit_app.py"

# 406 에러 우회를 위한 강력한 헤더 위장 코드
fix_code = """import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class EbcCrawler:
    def __init__(self):
        self.session = requests.Session()
        # [핵심] 406 에러를 피하기 위한 '완벽한 정장' 입기
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://m.ebcblue.com/bbs/login.php',
            'Origin': 'https://m.ebcblue.com',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
        self.login_action_url = "https://m.ebcblue.com/bbs/login_check.php"
        self.login_page_url = "https://m.ebcblue.com/bbs/login.php"

    def login(self, user_id, user_pw):
        try:
            # 1. 로그인 페이지 방문 (쿠키 굽기)
            page_res = self.session.get(self.login_page_url, headers=self.headers, verify=False)
            
            # 2. 숨겨진 토큰 등 모든 데이터 긁어모으기
            soup = BeautifulSoup(page_res.text, 'html.parser')
            login_data = {}
            for inp in soup.find_all('input'):
                if inp.get('name'):
                    login_data[inp.get('name')] = inp.get('value', '')

            # 3. 내 아이디/비번 입력
            login_data['mb_id'] = user_id
            login_data['mb_password'] = user_pw

            # 4. 제출 (POST)
            res = self.session.post(self.login_action_url, data=login_data, headers=self.headers, verify=False)
            res.encoding = res.apparent_encoding

            # 5. 결과 확인
            # 406 에러가 또 뜨는지 확인
            if res.status_code == 406:
                return False, "❌ 서버가 브라우저 설정을 거부했습니다 (406 Error). 보안이 매우 강력합니다."

            if '비밀번호가 틀립니다' in res.text:
                return False, "❌ 비밀번호가 틀렸습니다."
            if '존재하지 않는' in res.text:
                return False, "❌ 아이디가 없습니다."

            # 메인 페이지로 이동해서 최종 확인
            main_res = self.session.get('https://m.ebcblue.com/', headers=self.headers, verify=False)
            
            if '로그아웃' in main_res.text or 'logout' in main_res.text:
                return True, "✅ 로그인 성공! (보안 통과)"
            else:
                return False, f"⚠️ 로그인 실패. (상태코드: {res.status_code})"
                
        except Exception as e:
            return False, f"에러 발생: {str(e)}"

    def scan_links(self, url, keyword):
        st.info("🔍 페이지 스캔 중...")
        found_data = []
        try:
            res = self.session.get(url, headers=self.headers, verify=False)
            res.encoding = res.apparent_encoding
            soup = BeautifulSoup(res.text, 'html.parser')

            # 게시판 권한 체크
            if '권한이 없습니다' in res.text:
                st.error("⛔️ 해당 게시판에 접근 권한이 없습니다 (등급 부족).")
                return []

            for a in soup.find_all('a', href=True):
                text = a.get_text(strip=True)
                href = a['href']
                full_link = urljoin(url, href)

                if not keyword or (keyword and keyword in text):
                    if len(text) > 0 and 'javascript' not in href:
                        found_data.append({"제목": text, "링크": full_link})
            return found_data
        except: return []

# UI 구성
st.set_page_config(page_title="MOIM 보안 로그인", layout="wide")
st.title("🛡️ MOIM 번역기 : 보안 우회 모드")

with st.sidebar:
    st.header("로그인")
    user_id = st.text_input("아이디", key="uid")
    user_pw = st.text_input("비밀번호", type="password", key="upw")

st.subheader("1. 검색 설정")
url = st.text_input("타겟 URL", "http://m.ebcblue.com/")
keyword = st.text_input("찾을 키워드", placeholder="비워두면 전체 검색")

if st.button("🚀 로그인하고 검색하기"):
    if not user_id or not user_pw:
        st.error("아이디와 비밀번호를 입력해주세요.")
    else:
        crawler = EbcCrawler()
        status = st.empty()
        status.info("🛡️ 보안 헤더 장착 후 로그인 시도 중...")
        
        is_success, message = crawler.login(user_id, user_pw)
        
        if is_success:
            status.success(message)
            results = crawler.scan_links(url, keyword)
            if results:
                st.success(f"🎉 {len(results)}개의 결과를 찾았습니다!")
                
                table_head = "| 제목 | 바로가기 |\\n"
                table_div = "|---|---|\\n"
                md_table = table_head + table_div
                for row in results:
                    row_str = f"| {row['제목']} | [이동하기]({row['링크']}) |\\n"
                    md_table += row_str
                st.markdown(md_table)
            else:
                st.warning("결과가 없습니다.")
        else:
            status.error(message)
"""

with open(target_file, "w", encoding="utf-8") as f:
    f.write(fix_code)

print("✅ [패치 완료] 406 에러 방지용 헤더가 적용되었습니다.")
