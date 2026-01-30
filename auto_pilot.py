import os

target_file = "backend/scripts/crawler.py"

crawler_code = """import requests
from bs4 import BeautifulSoup
import streamlit as st
from urllib.parse import urljoin, quote, urlparse, parse_qs
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class EbcCrawler:
    def __init__(self, **kwargs):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://m.ebcblue.com/'
        }

    def _init_driver(self): pass
    def close(self): pass

    def get_categorized_links(self, url, keyword=None, *args, **kwargs):
        st.info(f"📡 분석 시작: {url}")
        
        # 1차 시도: 현재 페이지에서 바로 찾기
        links = self.get_post_links(url, keyword, depth=0)
        
        # 2차 시도: 없으면 게시판을 찾아서 들어가기 (자율주행)
        if not links:
            st.warning("⚠️ 현재 페이지에 게시글이 없습니다. 하위 게시판을 탐색합니다...")
            board_links = self._find_board_links(url)
            
            if board_links:
                target_board = board_links[0] # 첫 번째 게시판 선택
                st.success(f"🚀 [자율주행] 발견된 게시판으로 이동합니다: {target_board}")
                links = self.get_post_links(target_board, keyword, depth=1)
            else:
                st.error("❌ 이동할 수 있는 게시판을 찾지 못했습니다.")

        return {'notice': [], 'normal': links}

    def _find_board_links(self, url):
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
            return boards
        except: return []

    def get_post_links(self, url, keyword=None, depth=0):
        links = []
        try:
            res = self.session.get(url, headers=self.headers, verify=False, timeout=15)
            res.encoding = res.apparent_encoding
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # 진단 로그 (메인 페이지일 때만 출력)
            if depth == 0:
                all_a = soup.find_all('a', href=True)
                with st.expander(f"🕵️‍♂️ 페이지 진단 (링크 {len(all_a)}개)", expanded=True):
                    for a in all_a[:3]:
                        st.text(f"[{a.get_text(strip=True)}] -> {a['href']}")

            for a in soup.find_all('a', href=True):
                href = a['href']
                text = a.get_text(strip=True)
                full_link = urljoin(url, href)
                
                # wr_id (게시글) 찾기
                if 'wr_id=' in href:
                    if any(x in href for x in ['write', 'update', 'delete', 'search', 'login']): continue
                    
                    # 키워드 필터링
                    if keyword:
                        if keyword.lower() in text.lower() or keyword.lower() in full_link.lower():
                            if full_link not in links: links.append(full_link)
                    else:
                        if full_link not in links: links.append(full_link)
            
            if links:
                st.success(f"🎯 {len(links)}개의 게시글을 찾았습니다! (출처: {url})")
            
            return links
        except Exception as e:
            if depth == 0: st.error(f"❌ 오류: {e}")
            return []

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

print("✅ 자율주행(Auto-Pilot) 시스템 탑재 완료!")
