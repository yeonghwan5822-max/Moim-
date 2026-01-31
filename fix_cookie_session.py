import os

target_file = "backend/streamlit_app.py"

# 세션 쿠키를 먼저 챙기고 로그인하는 '정석' 코드
cookie_code = """import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import urllib3
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class EbcCrawler:
    def __init__(self):
        # [중요] 세션 객체 생성 (이 가방 안에 쿠키를 자동으로 저장함)
        self.session = requests.Session()
        
        # [전략] 복잡한 헤더 다 빼고, 가장 안전한 아이폰으로 위장
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
            'Referer': 'https://m.ebcblue.com/bbs/login.php',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        self.login_page = "https://m.ebcblue.com/bbs/login.php"
        self.login_action = "https://m.ebcblue.com/bbs/login_check.php"

    def login(self, user_id, user_pw):
        try:
            # 1. [쿠키 획득] 로그인 페이지에 먼저 방문해서 '세션 쿠키'를 받아옴
            # 이걸 안 하면 406 에러가 뜸
            self.session.get(self.login_page, headers=self.headers, verify=False)
            
            # 2. 데이터 준비
            data = {
                'mb_id': user_id,
                'mb_password': user_pw,
                'url': 'https://m.ebcblue.com/'
            }
            
            # 3. 로그인 시도 (자동으로 아까 받은 쿠키를 같이 냄)
            res = self.session.post(self.login_action, data=data, headers=self.headers, verify=False)
            res.encoding = res.apparent_encoding

            # 4. 결과 진단
            if res.status_code == 406:
                return False, "❌ 여전히 406 에러입니다. (서버 보안이 매우 강력함)"
            
            if res.status_code != 200:
                return False, f"⚠️ 서버 오류: {res.status_code}"

            if '비밀번호가 틀립니다' in res.text:
                return False, "❌ 비밀번호가 틀렸습니다."
            if '존재하지 않는' in res.text:
                return False, "❌ 아이디가 없습니다."

            # 5. 최종 확인 (로그아웃 버튼 찾기)
            main_res = self.session.get('https://m.ebcblue.com/', headers=self.headers, verify=False)
            
            if '로그아웃' in main_res.text or 'logout' in main_res.text:
                return True, "✅ 로그인 성공! (쿠키 전략 통함)"
            else:
                return False, "⚠️ 로그인 실패 (화면 변화 없음). 아이디/비번을 다시 확인하세요."
                
        except Exception as e:
            return False, f"시스템 에러: {str(e)}"

    def scan_links(self, url, keyword):
        st.info("🔍 페이지 스캔 중...")
        found_data = []
        try:
            res = self.session.get(url, headers=self.headers, verify=False)
            res.encoding = res.apparent_encoding
            soup = BeautifulSoup(res.text, 'html.parser')

            for a in soup.find_all('a', href=True):
                text = a.get_text(strip=True)
                href = a['href']
                full_link = urljoin(url, href)

                # 키워드가 있거나 없거나
                if not keyword or (keyword and keyword in text):
                    # 자바스크립트 링크 제외
                    if len(text) > 0 and 'javascript' not in href:
                        found_data.append({"제목": text, "링크": full_link})
            return found_data
        except: return []

# UI 구성
st.set_page_config(page_title="MOIM 쿠키 해결사", layout="wide")
st.title("🍪 MOIM 번역기 : 쿠키 해결 모드")

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
        status.info("🍪 쿠키 획득 후 입장 시도 중...")
        
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
    f.write(cookie_code)

print("✅ [수정 완료] 이번엔 중복이 아닙니다. 쿠키 로직이 적용되었습니다.")
