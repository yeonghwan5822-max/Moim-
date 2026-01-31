import os

target_file = "backend/streamlit_app.py"

# 모바일 전용 사이트 맞춤형 헤더 (갤럭시 S23 위장)
stealth_code = """import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import urllib3
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class EbcCrawler:
    def __init__(self):
        self.session = requests.Session()
        # [핵심] 완벽한 모바일(갤럭시) 기기로 위장
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 13; SM-S918N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://m.ebcblue.com/bbs/login.php',
            'Origin': 'https://m.ebcblue.com',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document'
        }
        self.login_action_url = "https://m.ebcblue.com/bbs/login_check.php"
        self.login_page_url = "https://m.ebcblue.com/bbs/login.php"

    def login(self, user_id, user_pw):
        try:
            # 1. 로그인 페이지 방문 (자연스럽게 보이기 위해 1초 대기)
            self.session.get(self.login_page_url, headers=self.headers, verify=False)
            time.sleep(1)
            
            # 2. 로그인 시도
            data = {
                'mb_id': user_id,
                'mb_password': user_pw,
                'url': 'https://m.ebcblue.com/'
            }
            res = self.session.post(self.login_action_url, data=data, headers=self.headers, verify=False)
            res.encoding = res.apparent_encoding

            # 3. 406 에러 체크
            if res.status_code == 406:
                return False, "❌ 서버가 모바일 기기 위장도 눈치챘습니다 (406 Error). 매우 까다로운 서버입니다."

            # 4. 결과 확인
            if '비밀번호가 틀립니다' in res.text:
                return False, "❌ 비밀번호가 틀렸습니다."
            if '존재하지 않는' in res.text:
                return False, "❌ 아이디가 없습니다."

            # 메인 페이지 확인
            main_res = self.session.get('https://m.ebcblue.com/', headers=self.headers, verify=False)
            
            if '로그아웃' in main_res.text or 'logout' in main_res.text:
                return True, "✅ 로그인 성공! (모바일 위장 통과)"
            else:
                # 로그인 실패 시 HTML 일부를 보여줘서 원인 파악
                return False, f"⚠️ 로그인 실패 (상태코드: {res.status_code})."
                
        except Exception as e:
            return False, f"에러 발생: {str(e)}"

    def scan_links(self, url, keyword):
        st.info("🔍 모바일 화면 스캔 중...")
        found_data = []
        try:
            res = self.session.get(url, headers=self.headers, verify=False)
            res.encoding = res.apparent_encoding
            soup = BeautifulSoup(res.text, 'html.parser')

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
st.set_page_config(page_title="MOIM 모바일 스텔스", layout="wide")
st.title("📱 MOIM 번역기 : 모바일 스텔스 모드")

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
        status.info("📱 갤럭시폰으로 위장하여 접속 중...")
        
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
    f.write(stealth_code)

print("✅ [패치 완료] 완벽한 모바일 기기로 위장했습니다.")
