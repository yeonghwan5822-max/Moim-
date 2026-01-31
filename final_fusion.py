import os

# 파일 경로: 메인 앱 파일에 모든 기능을 몰아넣습니다.
target_file = "backend/streamlit_app.py"

fusion_code = """import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import urllib3

# SSL 경고 무시
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==========================================
# 1. 내장 크롤러 (EbcCrawler) 정의
# ==========================================
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

    def get_links(self, url, keyword=None):
        # 1. 현재 페이지 스캔
        links = self._scan(url, keyword)
        if links: return links

        # 2. 없으면 전체 게시판 자동 순찰
        st.info("현재 페이지에 글이 없어, 전체 게시판을 순찰합니다...")
        boards = self._find_boards(url)
        all_links = []
        
        status = st.empty()
        prog = st.progress(0)
        
        for i, board in enumerate(boards):
            if 'calendar' in board: continue
            
            board_name = board.split('bo_table=')[-1]
            status.text(f"🏃 {board_name} 게시판 확인 중...")
            prog.progress((i+1)/len(boards))
            
            found = self._scan(board, keyword)
            if found: all_links.extend(found)
            
        status.empty()
        prog.empty()
        return list(set(all_links))

    def _find_boards(self, url):
        try:
            res = self.session.get(url, headers=self.headers, verify=False)
            res.encoding = res.apparent_encoding
            soup = BeautifulSoup(res.text, 'html.parser')
            boards = []
            for a in soup.find_all('a', href=True):
                if 'board.php' in a['href'] and 'bo_table=' in a['href']:
                    boards.append(urljoin(url, a['href']))
            return list(set(boards))
        except: return []

    def _scan(self, url, keyword):
        links = []
        try:
            res = self.session.get(url, headers=self.headers, verify=False)
            res.encoding = res.apparent_encoding
            soup = BeautifulSoup(res.text, 'html.parser')
            for a in soup.find_all('a', href=True):
                href = a['href']
                if 'wr_id=' in href and 'bo_table=' in href:
                    if any(x in href for x in ['write', 'update', 'delete', 'search']): continue
                    full_link = urljoin(url, href)
                    text = a.get_text(strip=True)
                    if keyword:
                        if keyword in text or keyword in full_link: links.append(full_link)
                    else:
                        links.append(full_link)
            return links
        except: return []

# ==========================================
# 2. 화면 (UI) 구성
# ==========================================
st.set_page_config(page_title="MOIM 번역기 (Final)", layout="wide")
st.title("🔐 MOIM 번역기 : 회원 전용 모드")

with st.sidebar:
    st.header("로그인")
    user_id = st.text_input("아이디", key="uid")
    user_pw = st.text_input("비밀번호", type="password", key="upw")

url = st.text_input("타겟 URL", "http://m.ebcblue.com/")
keyword = st.text_input("키워드 (선택)")

if st.button("🚀 로그인하고 게시물 찾기"):
    if not user_id or not user_pw:
        st.error("왼쪽 사이드바에서 로그인을 먼저 해주세요.")
    else:
        crawler = EbcCrawler() # 위에서 정의한 클래스 바로 사용
        with st.spinner("로그인 중..."):
            if crawler.login(user_id, user_pw):
                st.success("✅ 로그인 성공!")
                
                results = crawler.get_links(url, keyword)
                if results:
                    st.success(f"🎉 {len(results)}개의 게시물을 찾았습니다!")
                    for link in results:
                        st.write(f"- {link}")
                else:
                    st.warning("게시물을 찾지 못했습니다.")
            else:
                st.error("❌ 로그인 실패. 아이디/비번을 확인하세요.")
"""

with open(target_file, "w", encoding="utf-8") as f:
    f.write(fusion_code)

print("✅ [통합 완료] 이제 파일 충돌로 인한 에러는 발생하지 않습니다!")
