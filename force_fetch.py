import os

target_file = "backend/streamlit_app.py"

# wr_id 조건 제거 + 모든 링크 보여주는 디버깅 모드 추가
fusion_code = """import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class EbcCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
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

    def get_links(self, url, keyword=None):
        st.info("🕵️‍♂️ '필터 없이' 홈 화면의 모든 링크를 긁어옵니다...")
        
        try:
            res = self.session.get(url, headers=self.headers, verify=False)
            res.encoding = res.apparent_encoding
            soup = BeautifulSoup(res.text, 'html.parser')
            
            all_found = []
            debug_list = []
            
            # 모든 a 태그 검사
            for a in soup.find_all('a', href=True):
                href = a['href']
                text = a.get_text(strip=True)
                full_link = urljoin(url, href)
                
                # [수정된 조건] wr_id가 없어도 board.php만 있으면 일단 의심!
                if 'board.php' in href:
                    debug_list.append(f"[{text}] -> {href}")
                    
                    # 쓰기/삭제/수정 등은 제외
                    if any(x in href for x in ['write', 'update', 'delete', 'search', 'logout']): 
                        continue
                    
                    if keyword:
                        if keyword in text: all_found.append(full_link)
                    else:
                        all_found.append(full_link)

            # 디버깅용: 발견된 링크들 화면에 출력 (사용자가 볼 수 있게)
            with st.expander("🔎 크롤러가 발견한 원본 링크들 (클릭해서 확인)"):
                st.write(f"총 {len(debug_list)}개의 링크를 감지했습니다.")
                for d in debug_list:
                    st.text(d)

            return list(set(all_found))

        except Exception as e:
            st.error(f"에러 발생: {e}")
            return []

# UI 구성
st.set_page_config(page_title="MOIM 강제 수집기", layout="wide")
st.title("🚜 MOIM 번역기 : 강제 수집 모드")

with st.sidebar:
    st.header("로그인")
    user_id = st.text_input("아이디", key="uid")
    user_pw = st.text_input("비밀번호", type="password", key="upw")

url = st.text_input("타겟 URL", "http://m.ebcblue.com/")
keyword = st.text_input("키워드 (비워두세요!)", placeholder="엔터키를 눌러 비워두세요")

if st.button("🚀 로그인하고 강제로 긁어오기"):
    if not user_id or not user_pw:
        st.error("아이디와 비밀번호를 입력해주세요.")
    else:
        crawler = EbcCrawler()
        if crawler.login(user_id, user_pw):
            st.success("로그인 성공! 분석 시작...")
            results = crawler.get_links(url, keyword)
            
            if results:
                st.success(f"🎉 필터를 끄고 {len(results)}개의 글을 찾았습니다!")
                for link in results:
                    st.write(f"- {link}")
            else:
                st.error("여전히 링크가 안 잡힙니다. 아래 '크롤러가 발견한 원본 링크들'을 열어서 캡쳐해주세요.")
        else:
            st.error("로그인 실패")
"""

with open(target_file, "w", encoding="utf-8") as f:
    f.write(fusion_code)

print("✅ [강제 수집 패치] 완료. 이제 숨겨진 링크도 다 보입니다.")
