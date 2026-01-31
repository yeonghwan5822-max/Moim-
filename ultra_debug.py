import os

target_file = "backend/streamlit_app.py"

# HTML 소스 자체를 뒤져서 키워드를 찾는 초정밀 진단 코드
debug_code = """import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class EbcCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://m.ebcblue.com/'
        }
        self.login_url = "https://m.ebcblue.com/bbs/login_check.php"

    def login(self, user_id, user_pw):
        try:
            data = {'mb_id': user_id, 'mb_password': user_pw, 'url': 'https://m.ebcblue.com/'}
            res = self.session.post(self.login_url, data=data, headers=self.headers, verify=False)
            if "비밀번호가 틀립니다" in res.text or "존재하지 않는" in res.text:
                return False
            return True
        except: return False

    def deep_scan(self, url, keyword):
        st.info("🔬 페이지를 해부하는 중입니다...")
        
        try:
            res = self.session.get(url, headers=self.headers, verify=False)
            res.encoding = res.apparent_encoding
            html_content = res.text
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 1. HTML 소스 전체에서 키워드 검색 (가장 확실한 방법)
            st.write(f"### 1. 소스코드 정밀 검색 결과 (키워드: '{keyword}')")
            if keyword and keyword in html_content:
                st.success(f"✅ HTML 소스코드 안에서 '{keyword}'라는 단어를 발견했습니다!")
                st.text("아래 '발견된 위치'를 확인하세요.")
                
                # 키워드 주변 100글자 보여주기
                idx = html_content.find(keyword)
                start = max(0, idx - 100)
                end = min(len(html_content), idx + 100)
                snippet = html_content[start:end]
                st.code(snippet, language='html')
            elif keyword:
                st.error(f"❌ HTML 소스코드 전체를 뒤졌지만 '{keyword}'라는 단어가 아예 없습니다.")
                st.warning("오타가 있거나, 로그인이 풀려서 다른 화면이 보이는 것일 수 있습니다.")
            
            # 2. 모든 링크(a 태그) 전수 조사
            st.divider()
            st.write("### 2. 페이지 내 모든 링크 목록 (필터 없음)")
            
            links = soup.find_all('a', href=True)
            found_data = []
            
            for i, a in enumerate(links):
                text = a.get_text(strip=True)
                href = a['href']
                
                # 키워드가 있거나, 키워드가 비어있으면 다 넣기
                if not keyword or (keyword and keyword in text):
                    found_data.append({"No": i+1, "텍스트": text, "주소(href)": href})

            if found_data:
                st.success(f"🔍 총 {len(found_data)}개의 링크를 찾았습니다.")
                st.table(found_data)
            else:
                st.warning("링크 목록에서도 키워드를 찾지 못했습니다.")

        except Exception as e:
            st.error(f"분석 중 에러 발생: {e}")

# UI 구성
st.set_page_config(page_title="MOIM 초정밀 진단", layout="wide")
st.title("🔬 MOIM 번역기 : 초정밀 내시경 모드")

with st.sidebar:
    st.header("로그인")
    user_id = st.text_input("아이디", key="uid")
    user_pw = st.text_input("비밀번호", type="password", key="upw")

url = st.text_input("타겟 URL", "http://m.ebcblue.com/")
keyword = st.text_input("확인할 키워드 (예: 실습)", "실습")

if st.button("🚀 로그인하고 해부 시작"):
    if not user_id or not user_pw:
        st.error("아이디와 비밀번호를 입력해주세요.")
    else:
        crawler = EbcCrawler()
        if crawler.login(user_id, user_pw):
            st.success("로그인 성공! 분석을 시작합니다.")
            crawler.deep_scan(url, keyword)
        else:
            st.error("로그인 실패")
"""

with open(target_file, "w", encoding="utf-8") as f:
    f.write(debug_code)

print("✅ [초정밀 진단 패치] 완료. 이제 소스코드까지 뒤집니다.")

