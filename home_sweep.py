import os

target_file = "backend/streamlit_app.py"

fusion_code = """import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import urllib3

# SSL 경고 무시
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

    def get_links(self, url, keyword=None, fetch_all_home=True):
        all_links = []
        
        # 1. [핵심] 홈 화면 싹쓸이 (키워드 무시 옵션)
        st.info("🏠 홈 화면에 보이는 게시글을 우선 수집합니다...")
        home_links = self._scan(url, keyword if not fetch_all_home else None)
        
        if home_links:
            st.success(f"✅ 홈 화면에서 {len(home_links)}개의 최신 글을 확보했습니다!")
            all_links.extend(home_links)
        else:
            st.warning("홈 화면에서 게시글을 찾지 못했습니다. 게시판 순찰로 넘어갑니다.")

        # 2. 전체 게시판 자동 순찰
        st.divider()
        st.info("🔍 나머지 게시판들을 순찰합니다...")
        boards = self._find_boards(url)
        
        status = st.empty()
        prog = st.progress(0)
        
        for i, board in enumerate(boards):
            if 'calendar' in board: continue
            
            board_name = board.split('bo_table=')[-1]
            status.text(f"🏃 {board_name} 게시판 확인 중...")
            prog.progress((i+1)/len(boards))
            
            # 게시판 내부 글은 키워드 적용
            found = self._scan(board, keyword)
            if found: all_links.extend(found)
            
        status.empty()
        prog.empty()
        
        # 중복 제거 후 반환
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
                # wr_id가 있으면 무조건 게시글로 간주
                if 'wr_id=' in href:
                    # 글쓰기, 수정, 삭제 등 불필요한 링크 제외
                    if any(x in href for x in ['write', 'update', 'delete', 'search']): continue
                    
                    full_link = urljoin(url, href)
                    text = a.get_text(strip=True)
                    
                    if keyword:
                        # 키워드가 있으면 제목이나 링크에 포함되어야 함
                        if keyword in text or keyword in full_link: links.append(full_link)
                    else:
                        # 키워드 없으면 무조건 수집
                        links.append(full_link)
            return links
        except: return []

# ==========================================
# UI 구성
# ==========================================
st.set_page_config(page_title="MOIM 번역기 (Final)", layout="wide")
st.title("🔐 MOIM 번역기 : 싹쓸이 모드")

with st.sidebar:
    st.header("로그인")
    user_id = st.text_input("아이디", key="uid")
    user_pw = st.text_input("비밀번호", type="password", key="upw")

st.write("### 1. 크롤링 설정")
col1, col2 = st.columns([3, 1])
with col1:
    url = st.text_input("타겟 URL", "http://m.ebcblue.com/")
with col2:
    keyword = st.text_input("키워드 (선택사항)", placeholder="예: 공지")

# [새 기능] 체크박스 추가
fetch_all_home = st.checkbox("✅ 홈 화면에 보이는 글은 키워드 상관없이 다 가져오기", value=True)

if st.button("🚀 로그인하고 게시물 찾기"):
    if not user_id or not user_pw:
        st.error("왼쪽 사이드바에서 로그인을 먼저 해주세요.")
    else:
        crawler = EbcCrawler()
        with st.spinner("로그인 중..."):
            if crawler.login(user_id, user_pw):
                st.success("로그인 성공!")
                
                # 체크박스 옵션(fetch_all_home) 전달
                results = crawler.get_links(url, keyword, fetch_all_home)
                
                if results:
                    st.success(f"🎉 총 {len(results)}개의 게시물을 찾았습니다!")
                    st.write("---")
                    for link in results:
                        st.write(f"- {link}")
                else:
                    st.error("게시물을 찾지 못했습니다. 키워드를 지우고 다시 시도해보세요.")
            else:
                st.error("로그인 실패. 아이디/비번을 확인하세요.")
"""

with open(target_file, "w", encoding="utf-8") as f:
    f.write(fusion_code)

print("✅ [홈 화면 싹쓸이] 기능이 추가되었습니다!")
