import os

# 1. 설치 에러 방지를 위한 깨끗한 라이브러리 목록 (requirements.txt)
# 설치 실패 확률이 높은 무거운 라이브러리는 일단 제외하고 필수 항목만 넣었습니다.
requirements = """streamlit
requests
beautifulsoup4
python-dotenv
urllib3
"""

# 2. 크롤러 코드 (crawler.py) - SSL 우회 및 범용 검색 기능 포함
crawler_code = """import requests
from bs4 import BeautifulSoup
import streamlit as st
from urllib.parse import urljoin
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class EbcCrawler:
    def __init__(self, **kwargs):
        self.session = requests.Session()
        self.headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1'}

    def _init_driver(self): pass
    def close(self): pass

    def get_categorized_links(self, url, keyword=None, *args, **kwargs):
        st.info(f"🌐 탐색 중: {url}")
        return {'notice': [], 'normal': self.get_post_links(url, keyword)}

    def get_post_links(self, url, keyword=None):
        links = []
        try:
            res = self.session.get(url, headers=self.headers, verify=False, timeout=15)
            soup = BeautifulSoup(res.content, 'html.parser')
            for a in soup.find_all('a', href=True):
                href = a['href']
                if 'wr_id=' in href and 'bo_table=' in href:
                    if any(x in href for x in ['write', 'update', 'delete']): continue
                    full_link = urljoin(url, href)
                    if not keyword or (keyword.lower() in a.get_text().lower() or keyword.lower() in full_link.lower()):
                        if full_link not in links: links.append(full_link)
            st.success(f"🎯 {len(links)}개의 게시물을 찾았습니다.")
            return links
        except Exception as e:
            st.error(f"❌ 접속 에러: {e}")
            return []

    def get_post_content(self, url):
        try:
            res = self.session.get(url, headers=self.headers, verify=False, timeout=10)
            soup = BeautifulSoup(res.content, 'html.parser')
            title = soup.find(['h1', 'h2', 'title'])
            content = soup.find(id="bo_v_con") or soup.find(class_="view-content")
            return {
                'title': title.get_text(strip=True) if title else "제목 없음",
                'content': content.get_text(strip=True) if content else "본문 없음",
                'date': '2026-01-31'
            }
        except: return {'title': 'Error', 'content': '', 'date': ''}
"""

# 파일 쓰기
os.makedirs("backend/scripts", exist_ok=True)
with open("backend/requirements.txt", "w", encoding="utf-8") as f:
    f.write(requirements)
with open("backend/scripts/crawler.py", "w", encoding="utf-8") as f:
    f.write(crawler_code)
# 설치 오류를 일으킬 수 있는 packages.txt는 비웁니다.
with open("backend/packages.txt", "w") as f:
    f.write("")

print("✅ 복구 준비 완료! 이제 배포 명령어를 입력하세요.")
