import os

target_file = "backend/scripts/crawler.py"

crawler_code = """import requests
from bs4 import BeautifulSoup
import streamlit as st
from urllib.parse import urljoin, quote
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class EbcCrawler:
    def __init__(self, headless=True):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Referer': 'https://m.ebcblue.com/'
        }

    def _init_driver(self): pass
    def close(self): pass

    def get_categorized_links(self, url, keyword=None, *args, **kwargs):
        st.info(f"🌐 대상 사이트 정밀 스캔 중: {url}")
        raw_links = self.get_post_links(url, keyword)
        return {'notice': [], 'normal': raw_links}

    def get_post_links(self, url, keyword=None):
        links = []
        try:
            # 1. SSL 인증서 검사 무시하고 데이터 가져오기
            res = self.session.get(url, headers=self.headers, verify=False, timeout=15)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # 2. 게시판의 모든 '리스트 아이템' 또는 '링크' 탐색
            # 그누보드 모바일은 보통 <li> 안에 제목과 링크가 있습니다.
            items = soup.find_all(['li', 'tr', 'a']) 
            
            for item in items:
                # 해당 영역 안에 링크(<a>)가 있는지 확인
                a_tag = item if item.name == 'a' else item.find('a', href=True)
                if not a_tag or 'href' not in a_tag.attrs:
                    continue
                
                href = a_tag['href']
                text = item.get_text(strip=True) # 아이템 전체 텍스트를 가져와서 검사
                
                # 게시글 상세 페이지 패턴 (wr_id) 확인
                if 'wr_id=' in href and 'bo_table=' in href:
                    # 불필요한 링크 제외
                    if any(x in href for x in ['write', 'update', 'delete', 'search']):
                        continue
                        
                    full_link = urljoin(url, href)
                    
                    # [핵심] 키워드 매칭 로직 (제목 또는 전체 텍스트에 키워드가 있는지 확인)
                    if not keyword:
                        if full_link not in links: links.append(full_link)
                    elif keyword in text or keyword in full_link:
                        if full_link not in links: links.append(full_link)
            
            # 중복 제거
            final_links = list(dict.fromkeys(links))
            st.success(f"🎯 '{keyword if keyword else '전체'}' 키워드 게시물 {len(final_links)}개 발견!")
            return final_links

        except Exception as e:
            st.error(f"❌ 데이터 추출 실패: {e}")
            return []

    def get_post_content(self, url):
        try:
            res = self.session.get(url, headers=self.headers, verify=False, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')
            # 모바일 게시판용 본문 영역 탐색
            title = soup.find(['h1', 'h2', 'title'])
            content = soup.find(id=\"bo_v_con\") or soup.find(class_=\"view-content\") or soup.body
            return {
                'title': title.get_text(strip=True) if title else "제목 없음",
                'content': content.get_text(strip=True) if content else "본문 없음",
                'date': '2026-01-30'
            }
        except: return {'title': 'Error', 'content': '', 'date': ''}
"""

with open(target_file, "w", encoding="utf-8") as f:
    f.write(crawler_code)

print("✅ 초정밀 저인망 크롤러가 준비되었습니다!")
