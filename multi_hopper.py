import os

target_file = "backend/scripts/crawler.py"

crawler_code = """import requests
from bs4 import BeautifulSoup
import streamlit as st
from urllib.parse import urljoin
import urllib3
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class EbcCrawler:
    def __init__(self, **kwargs):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
            'Referer': 'https://m.ebcblue.com/'
        }

    def _init_driver(self): pass
    def close(self): pass

    def get_categorized_links(self, url, keyword=None, *args, **kwargs):
        st.info(f"📡 탐색 시작: {url}")
        
        # 1. 입력된 URL에서 바로 시도
        links = self.get_post_links(url, keyword, silent=True)
        if links:
            return {'notice': [], 'normal': links}
            
        # 2. 실패 시, 메인 페이지에서 다른 게시판 목록 수집 (멀티 호퍼 가동)
        st.warning("⚠️ 현재 페이지에서 소득이 없어, 다른 게시판들을 순찰합니다...")
        board_list = self._find_all_boards(url)
        
        if not board_list:
            st.error("❌ 이동할 수 있는 게시판을 찾지 못했습니다.")
            return {'notice': [], 'normal': []}

        # 3. 발견된 게시판들을 하나씩 순회
        success_links = []
        progress_bar = st.progress(0)
        
        for i, board_url in enumerate(board_list):
            # 'calendar'(달력) 같은 특수 게시판은 건너뛰기 (효율성)
            if 'calendar' in board_url: continue
            
            # 진행률 표시
            progress_bar.progress((i + 1) / len(board_list))
            st.write(f"🏃 이동 중: ...{board_url[-20:]}")
            
            # 접속 시도
            found_links = self.get_post_links(board_url, keyword, silent=True)
            
            if found_links:
                st.success(f"🎉 찾았다! [게시판: {board_url}]에서 {len(found_links)}개 발견!")
                success_links = found_links
                break # 하나라도 찾으면 즉시 중단하고 결과 반환
            
            time.sleep(0.5) # 서버 부하 방지

        progress_bar.empty()
        
        if not success_links:
            st.error("😭 모든 방을 다 뒤졌는데 게시글을 못 찾았습니다.")
            
        return {'notice': [], 'normal': success_links}

    def _find_all_boards(self, url):
        # 메인 페이지에서 'board.php'가 들어간 모든 링크 추출
        try:
            res = self.session.get(url, headers=self.headers, verify=False, timeout=10)
            res.encoding = res.apparent_encoding
            soup = BeautifulSoup(res.text, 'html.parser')
            boards = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                if 'board.php' in href and 'bo_table=' in href:
                    full_link = urljoin(url, href)
                    if full_link not in boards:
                        boards.append(full_link)
            
            st.info(f"🔎 총 {len(boards)}개의 게시판 입구를 발견했습니다.")
            return boards
        except: return []

    def get_post_links(self, url, keyword=None, silent=False):
        links = []
        try:
            res = self.session.get(url, headers=self.headers, verify=False, timeout=10)
            res.encoding = res.apparent_encoding
            soup = BeautifulSoup(res.text, 'html.parser')
            
            for a in soup.find_all('a', href=True):
                href = a['href']
                # wr_id(게시글) 패턴 확인
                if 'wr_id=' in href:
                    if any(x in href for x in ['write', 'update', 'delete', 'search', 'login']): continue
                    
                    full_link = urljoin(url, href)
                    text = a.get_text(strip=True)
                    
                    if keyword:
                        if keyword.lower() in text.lower() or keyword.lower() in full_link.lower():
                            if full_link not in links: links.append(full_link)
                    else:
                        if full_link not in links: links.append(full_link)
            
            if not silent and links:
                st.success(f"🎯 {len(links)}개 수집 완료")
                
            return links
        except: return []

    def get_post_content(self, url):
        try:
            res = self.session.get(url, headers=self.headers, verify=False, timeout=10)
            res.encoding = res.apparent_encoding
            soup = BeautifulSoup(res.text, 'html.parser')
            title = soup.find(['h1', 'h2', 'title'])
            content = soup.find(id="bo_v_con") or soup.find(class_="view-content") or soup.body
            return {
                'title': title.get_text(strip=True) if title else "제목 없음",
                'content': content.get_text(strip=True) if content else "본문 없음",
                'date': '2026-01-31'
            }
        except: return {'title': 'Error', 'content': '', 'date': ''}
"""

with open(target_file, "w", encoding="utf-8") as f:
    f.write(crawler_code)

print("✅ 다중 게시판 순찰 시스템(Multi-Hopper) 장착 완료!")

