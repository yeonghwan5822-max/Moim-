import os

target_file = "backend/streamlit_app.py"

# 입력 실수 방지를 위한 UI 개선 버전
bypass_code = """import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class EbcCrawler:
    def __init__(self):
        self.session = requests.Session()
        # 아이폰으로 위장 (406 에러 방지용 안전한 헤더)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
            'Referer': 'https://m.ebcblue.com/'
        }

    def set_cookie(self, phpsessid):
        # 쿠키 주입
        cookie_obj = requests.cookies.create_cookie(
            domain='m.ebcblue.com',
            name='PHPSESSID',
            value=phpsessid
        )
        self.session.cookies.set_cookie(cookie_obj)

    def run_scan(self, url, keyword):
        st.info(f"🚀 '{url}' 로 접속을 시도합니다...")
        
        try:
            # 1. 접속 시도
            res = self.session.get(url, headers=self.headers, verify=False)
            res.encoding = res.apparent_encoding
            
            # 2. 결과 확인
            if '로그아웃' in res.text or 'logout' in res.text:
                st.success("✅ 로그인 상태 확인됨! (쿠키가 정상 작동 중)")
                
                soup = BeautifulSoup(res.text, 'html.parser')
                found_data = []
                
                # 3. 데이터 수집
                for a in soup.find_all('a', href=True):
                    text = a.get_text(strip=True)
                    href = a['href']
                    full_link = urljoin(url, href)

                    if not keyword or (keyword and keyword in text):
                        if len(text) > 0 and 'javascript' not in href:
                            found_data.append({"제목": text, "링크": full_link})
                
                return found_data
            else:
                st.error("❌ 로그인 실패. 쿠키 값이 만료되었거나 틀렸습니다.")
                st.warning("팁: 크롬에서 다시 F12를 눌러 새로운 'PHPSESSID'를 복사해오세요.")
                return []
                
        except Exception as e:
            st.error(f"접속 에러: {e}")
            return []

# ==========================================
# UI 구성 (헷갈림 방지)
# ==========================================
st.set_page_config(page_title="MOIM 최종 번역기", layout="wide")
st.title("🍪 MOIM 번역기 : 쿠키 모드 (Final)")

st.warning("👇 아래 두 칸을 정확히 채워주세요!")

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. 어디로 갈까요?")
    # 기본값을 미리 넣어둠 (수정할 필요 없음)
    url = st.text_input("접속할 주소 (URL)", value="http://m.ebcblue.com/")

with col2:
    st.subheader("2. 출입증(암호)은?")
    # 여기가 쿠키 넣는 곳!
    phpsessid = st.text_input("PHPSESSID 값 붙여넣기", placeholder="bk0gf... 같은 값을 여기에 넣으세요")

st.divider()
keyword = st.text_input("3. 찾을 단어 (예: 실습)", placeholder="비워두면 모든 글을 가져옵니다")

if st.button("🚀 입력 완료! 데이터 가져오기"):
    if not phpsessid:
        st.error("오른쪽 칸에 쿠키(PHPSESSID) 값을 넣어주세요!")
    else:
        crawler = EbcCrawler()
        crawler.set_cookie(phpsessid) # 쿠키 장착
        
        results = crawler.run_scan(url, keyword)
        
        if results:
            st.success(f"🎉 성공! {len(results)}개의 글을 찾았습니다.")
            
            # 표 그리기
            table_head = "| 제목 | 바로가기 |\\n|---|---|\\n"
            md_table = table_head
            for row in results:
                md_table += f"| {row['제목']} | [이동하기]({row['링크']}) |\\n"
            st.markdown(md_table)
        elif phpsessid:
            st.info("결과가 없습니다.")
"""

with open(target_file, "w", encoding="utf-8") as f:
    f.write(bypass_code)
