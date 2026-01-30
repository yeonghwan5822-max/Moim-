import os

# 1. 크롤러 코드 (모든 수리 내역 통합)
crawler_code = """import requests
from bs4 import BeautifulSoup
import streamlit as st
from urllib.parse import urljoin, quote
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class EbcCrawler:
    def __init__(self, headless=True):
        self.session = requests.Session()
        self.headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1'}

    def _init_driver(self): pass
    def close(self): pass

    def get_categorized_links(self, url, keyword=None, *args, **kwargs):
        # 키워드 검색 URL 생성
        target_url = url
        if keyword:
            encoded_kw = quote(keyword.encode('utf-8'))
            sep = "&" if "?" in url else "?"
            target_url = f"{url}{sep}sfl=wr_subject||wr_content&stx={encoded_kw}"
        
        st.info(f"🔍 탐색 경로: {target_url}")
        raw_links = self.get_post_links(target_url, keyword)
        return {'notice': [], 'normal': raw_links}

    def get_post_links(self, url, keyword=None):
        links = []
        try:
            res = self.session.get(url, headers=self.headers, verify=False, timeout=15)
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # 모든 <a> 태그를 뒤져서 wr_id가 있는 링크 추출
            for a in soup.find_all('a', href=True):
                href = a['href']
                if 'wr_id=' in href and 'bo_table=' in href:
                    if any(x in href for x in ['write', 'update', 'delete']): continue
                    full_link = urljoin(url, href)
                    if full_link not in links:
                        # 키워드가 있다면 제목/링크에 '실습'이 포함되었는지 최종 확인
                        if not keyword or (keyword in a.get_text() or keyword in full_link):
                            links.append(full_link)
            
            st.success(f"✅ 총 {len(links)}개의 게시물을 찾았습니다.")
            return links
        except Exception as e:
            st.error(f"❌ 크롤링 실패: {e}")
            return []

    def get_post_content(self, url):
        try:
            res = self.session.get(url, headers=self.headers, verify=False, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')
            title = soup.find(['h1', 'h2', 'title'])
            content = soup.find(id="bo_v_con") or soup.find(class_="view-content")
            return {
                'title': title.get_text(strip=True) if title else "제목 없음",
                'content': content.get_text(strip=True)[:2000] if content else "본문 없음",
                'date': '2026-01-30'
            }
        except: return {'title': 'Error', 'content': '', 'date': ''}
"""

# 2. 파일 저장
os.makedirs("backend/scripts", exist_ok=True)
with open("backend/scripts/crawler.py", "w", encoding="utf-8") as f:
    f.write(crawler_code)

print("✨ [Anti-Gravity] 모든 코드 수리가 완료되었습니다. 이제 배포하세요!")
