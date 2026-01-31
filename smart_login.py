import os

target_file = "backend/streamlit_app.py"

# 토큰 자동 확보 + 로그인 로직 강화
smart_code = """import streamlit as st
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
            'Referer': 'https://m.ebcblue.com/bbs/login.php',
            'Origin': 'https://m.ebcblue.com'
        }
        self.login_action_url = "https://m.ebcblue.com/bbs/login_check.php"
        self.login_page_url = "https://m.ebcblue.com/bbs/login.php"

    def login(self, user_id, user_pw):
        try:
            # [1단계] 로그인 페이지에 먼저 가서 '숨겨진 암호표(Token)' 줍기
            page_res = self.session.get(self.login_page_url, headers=self.headers, verify=False)
            soup = BeautifulSoup(page_res.text, 'html.parser')
            
            # 전송할 데이터 가방 준비
            login_data = {}
            
            # 페이지에 있는 모든 숨겨진 정보(hidden input)를 가방에 담기
            for inp in soup.find_all('input'):
                if inp.get('name'):
                    login_data[inp.get('name')] = inp.get('value', '')

            # [2단계] 사용자 아이디/비번을 가방에 덮어쓰기
            login_data['mb_id'] = user_id
            login_data['mb_password'] = user_pw
            
            # [3단계] 꽉 찬 가방을 들고 로그인 시도
            res = self.session.post(self.login_action_url, data=login_data, headers=self.headers, verify=False)
            res.encoding = res.apparent_encoding

            # [4단계] 결과 확인
            if '비밀번호가 틀립니다' in res.text:
                return False, "❌ 비밀번호가 틀렸습니다."
            if '존재하지 않는' in res.text:
                return False, "❌ 아이디가 없습니다."

            # 메인 페이지로 이동해서 확인
            main_res = self.session.get('https://m.ebcblue.com/', headers=self.headers, verify=False)
            
            # 로그아웃 버튼이 보이면 성공!
            if '로그아웃' in main_res.text or 'logout' in main_res.text:
                return True, "✅ 로그인 성공!"
            else:
                # 디버깅용: 왜 실패했는지 힌트 남기기
                return False, f"⚠️ 여전히 거부됨. (서버 응답: {res.status_code})"
                
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
st.set_page_config(page_title="MOIM 스마트 로그인", layout="wide")
st.title("🔐 MOIM 번역기 : 지능형 로그인 모드")

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
        status.info("🔑 암호표(Token) 확보 후 로그인 시도 중...")
        
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
    f.write(smart_code)

print("✅ [패치 완료] 숨겨진 토큰 처리 기능이 추가되었습니다.")
