import os

target_file = "backend/streamlit_app.py"

# 방문 후 로그인(Visit-First) 로직 + 상세 에러 리포팅
clinic_code = """import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class EbcCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
            'Referer': 'https://m.ebcblue.com/',
            'Origin': 'https://m.ebcblue.com'
        }
        self.login_url = "https://m.ebcblue.com/bbs/login_check.php"

    def login(self, user_id, user_pw):
        try:
            # [1단계] 메인 페이지 먼저 방문 (쿠키/세션 획득 - 중요!)
            self.session.get('https://m.ebcblue.com/', headers=self.headers, verify=False)
            
            # [2단계] 로그인 시도
            data = {'mb_id': user_id, 'mb_password': user_pw, 'url': 'https://m.ebcblue.com/'}
            res = self.session.post(self.login_url, data=data, headers=self.headers, verify=False)
            res.encoding = res.apparent_encoding # 한글 깨짐 방지

            # [3단계] 서버 응답 분석 (왜 실패했는지 확인)
            if '비밀번호가 틀립니다' in res.text:
                return False, "❌ 비밀번호가 틀렸다고 합니다."
            if '존재하지 않는' in res.text or '아이디가 없거나' in res.text:
                return False, "❌ 존재하지 않는 아이디라고 합니다."
            if '차단' in res.text:
                return False, "❌ 접속이 차단된 것 같습니다."

            # [4단계] 진짜 로그인 됐는지 재확인
            main_res = self.session.get('https://m.ebcblue.com/', headers=self.headers, verify=False)
            if '로그아웃' in main_res.text or 'logout' in main_res.text:
                return True, "✅ 로그인 성공!"
            else:
                # 로그인 성공 메시지도 없고, 에러도 없는데 로그인이 안 된 경우
                return False, "⚠️ 서버가 로그인을 무시했습니다. (알 수 없는 이유)"
                
        except Exception as e:
            return False, f"에러 발생: {str(e)}"

    def scan_links(self, url, keyword):
        st.info("🔍 페이지 스캔 중...")
        found_data = []
        try:
            res = self.session.get(url, headers=self.headers, verify=False)
            res.encoding = res.apparent_encoding
            soup = BeautifulSoup(res.text, 'html.parser')

            if keyword and keyword not in res.text:
                st.error(f"❌ '{keyword}' 단어 없음.")
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
st.set_page_config(page_title="MOIM 로그인 클리닉", layout="wide")
st.title("🩺 MOIM 번역기 : 로그인 정밀 진단")

with st.sidebar:
    st.header("로그인")
    user_id = st.text_input("아이디", key="uid")
    user_pw = st.text_input("비밀번호", type="password", key="upw")

st.subheader("1. 검색 설정")
url = st.text_input("타겟 URL", "http://m.ebcblue.com/")
keyword = st.text_input("찾을 키워드", placeholder="비워두면 전체 검색")

if st.button("🚀 로그인하고 원인 분석하기"):
    if not user_id or not user_pw:
        st.error("아이디와 비밀번호를 입력해주세요.")
    else:
        crawler = EbcCrawler()
        status = st.empty()
        status.info("🔑 로그인 시도 중 (방문 -> 로그인)...")
        
        # 상세 결과 받기
        is_success, message = crawler.login(user_id, user_pw)
        
        if is_success:
            status.success(message)
            results = crawler.scan_links(url, keyword)
            if results:
                st.success(f"🎉 {len(results)}개의 결과를 찾았습니다!")
                
                # 안전한 테이블 출력
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
            status.error(message) # 서버가 알려준 진짜 거절 사유 출력
"""import os

target_file = "backend/streamlit_app.py"

# 방문 후 로그인(Visit-First) 로직 + 상세 에러 리포팅
clinic_code = """import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class EbcCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
            'Referer': 'https://m.ebcblue.com/',
            'Origin': 'https://m.ebcblue.com'
        }
        self.login_url = "https://m.ebcblue.com/bbs/login_check.php"

    def login(self, user_id, user_pw):
        try:
            # [1단계] 메인 페이지 먼저 방문 (쿠키/세션 획득 - 중요!)
            self.session.get('https://m.ebcblue.com/', headers=self.headers, verify=False)
            
            # [2단계] 로그인 시도
            data = {'mb_id': user_id, 'mb_password': user_pw, 'url': 'https://m.ebcblue.com/'}
            res = self.session.post(self.login_url, data=data, headers=self.headers, verify=False)
            res.encoding = res.apparent_encoding # 한글 깨짐 방지

            # [3단계] 서버 응답 분석 (왜 실패했는지 확인)
            if '비밀번호가 틀립니다' in res.text:
                return False, "❌ 비밀번호가 틀렸다고 합니다."
            if '존재하지 않는' in res.text or '아이디가 없거나' in res.text:
                return False, "❌ 존재하지 않는 아이디라고 합니다."
            if '차단' in res.text:
                return False, "❌ 접속이 차단된 것 같습니다."

            # [4단계] 진짜 로그인 됐는지 재확인
            main_res = self.session.get('https://m.ebcblue.com/', headers=self.headers, verify=False)
            if '로그아웃' in main_res.text or 'logout' in main_res.text:
                return True, "✅ 로그인 성공!"
            else:
                # 로그인 성공 메시지도 없고, 에러도 없는데 로그인이 안 된 경우
                return False, "⚠️ 서버가 로그인을 무시했습니다. (알 수 없는 이유)"
                
        except Exception as e:
            return False, f"에러 발생: {str(e)}"

    def scan_links(self, url, keyword):
        st.info("🔍 페이지 스캔 중...")
        found_data = []
        try:
            res = self.session.get(url, headers=self.headers, verify=False)
            res.encoding = res.apparent_encoding
            soup = BeautifulSoup(res.text, 'html.parser')

            if keyword and keyword not in res.text:
                st.error(f"❌ '{keyword}' 단어 없음.")
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
st.set_page_config(page_title="MOIM 로그인 클리닉", layout="wide")
st.title("🩺 MOIM 번역기 : 로그인 정밀 진단")

with st.sidebar:
    st.header("로그인")
    user_id = st.text_input("아이디", key="uid")
    user_pw = st.text_input("비밀번호", type="password", key="upw")

st.subheader("1. 검색 설정")
url = st.text_input("타겟 URL", "http://m.ebcblue.com/")
keyword = st.text_input("찾을 키워드", placeholder="비워두면 전체 검색")

if st.button("🚀 로그인하고 원인 분석하기"):
    if not user_id or not user_pw:
        st.error("아이디와 비밀번호를 입력해주세요.")
    else:
        crawler = EbcCrawler()
        status = st.empty()
        status.info("🔑 로그인 시도 중 (방문 -> 로그인)...")
        
        # 상세 결과 받기
        is_success, message = crawler.login(user_id, user_pw)
        
        if is_success:
            status.success(message)
            results = crawler.scan_links(url, keyword)
            if results:
                st.success(f"🎉 {len(results)}개의 결과를 찾았습니다!")
                
                # 안전한 테이블 출력
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
            status.error(message) # 서버가 알려준 진짜 거절 사유 출력
"""

with open(target_file, "w", encoding="utf-8") as f:
    f.write(clinic_code)

print("✅ [클리닉 패치 완료] 이제 서버의 거절 사유를 알 수 있습니다.")
