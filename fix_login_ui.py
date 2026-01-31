import os

target_file = "backend/streamlit_app.py"

# 1. 로그인 검증 강화 + 2. 클릭 가능한 링크 테이블 기능 추가
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
        # 모바일 브라우저인 척 위장 (중요)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
            'Referer': 'https://m.ebcblue.com/',
            'Origin': 'https://m.ebcblue.com'
        }
        self.login_url = "https://m.ebcblue.com/bbs/login_check.php"

    def login(self, user_id, user_pw):
        try:
            # 1. 로그인 시도
            data = {'mb_id': user_id, 'mb_password': user_pw, 'url': 'https://m.ebcblue.com/'}
            self.session.post(self.login_url, data=data, headers=self.headers, verify=False)
            
            # 2. [핵심] 진짜 로그인이 됐는지 메인 페이지 가서 확인
            res = self.session.get('https://m.ebcblue.com/', headers=self.headers, verify=False)
            res.encoding = res.apparent_encoding
            
            # '로그아웃' 버튼이 있어야 진짜 로그인 된 것임
            if '로그아웃' in res.text or 'logout' in res.text:
                return True
            else:
                return False
        except: return False

    def scan_links(self, url, keyword):
        st.info("🔍 페이지를 스캔 중입니다...")
        found_data = []
        
        try:
            res = self.session.get(url, headers=self.headers, verify=False)
            res.encoding = res.apparent_encoding
            soup = BeautifulSoup(res.text, 'html.parser')

            # 1. HTML 전체에서 키워드 존재 여부 확인
            if keyword and keyword not in res.text:
                st.error(f"❌ 페이지 소스 코드 내에 '{keyword}'라는 단어가 없습니다.")
                st.warning("로그인이 되었음에도 안 보인다면, 해당 게시물이 1페이지에 없거나 권한이 없는 게시판일 수 있습니다.")
                return []

            # 2. 링크 수집 및 정리
            for a in soup.find_all('a', href=True):
                text = a.get_text(strip=True)
                href = a['href']
                full_link = urljoin(url, href)

                # 키워드가 있거나, 없으면 모두 수집
                if not keyword or (keyword and keyword in text):
                    # 자바스크립트나 빈 링크 제외
                    if len(text) > 0 and 'javascript' not in href:
                        found_data.append({
                            "제목": text,
                            "링크": full_link
                        })
            
            return found_data

        except Exception as e:
            st.error(f"에러: {e}")
            return []

# ==========================================
# UI 구성
# ==========================================
st.set_page_config(page_title="MOIM 번역기 (Final)", layout="wide")
st.title("🔐 MOIM 번역기 : 회원 전용 검색")

with st.sidebar:
    st.header("로그인")
    user_id = st.text_input("아이디", key="uid")
    user_pw = st.text_input("비밀번호", type="password", key="upw")

st.subheader("1. 검색 설정")
url = st.text_input("타겟 URL", "http://m.ebcblue.com/")
keyword = st.text_input("찾을 키워드 (예: 실습)", placeholder="비워두면 모든 링크를 보여줍니다")

if st.button("🚀 로그인하고 검색 시작"):
    if not user_id or not user_pw:
        st.error("아이디와 비밀번호를 입력해주세요.")
    else:
        crawler = EbcCrawler()
        status = st.empty()
        status.info("🔑 로그인 검증 중...")
        
        # 진짜 로그인이 되었는지 확인
        if crawler.login(user_id, user_pw):
            status.success("✅ 로그인 확인 완료! (로그아웃 버튼 감지됨)")
            
            results = crawler.scan_links(url, keyword)
            
            if results:
                st.success(f"🎉 '{keyword}' 관련 항목 {len(results)}개를 찾았습니다!")
                
                # [개선된 UI] 클릭 가능한 데이터프레임
                df = pd.DataFrame(results)
                
                # 링크를 클릭 가능한 형태로 변환하여 보여주기
                st.write("### 📋 검색 결과 (링크를 클릭하세요)")
                
                # 마크다운 표로 변환하여 출력 (Streamlit에서 링크 클릭 가능하게 하는 가장 확실한 방법)
                md_table = "| 제목 | 바로가기 |\n|---|---|\n"
                for row in results:
                    md_table += f"| {row['제목']} | [이동하기]({row['링크']}) |\n"
                
                st.markdown(md_table)
                
            else:
                st.warning("결과가 없습니다.")
        else:
            status.error("❌ 로그인 실패! (아이디/비번이 틀렸거나, 서버가 로그인을 거부했습니다)")
            st.caption("팁: '로그인' 버튼이 여전히 보이면 실패한 것입니다.")
"""

with open(target_file, "w", encoding="utf-8") as f:
    f.write(final_code)

print("✅ [패치 완료] 로그인 검증 강화 + 결과 테이블 디자인 개선")
