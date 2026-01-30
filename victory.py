import os

target_file = "backend/scripts/crawler.py"

crawler_code = """import requests
from bs4 import BeautifulSoup
import time
import streamlit as st
from urllib.parse import urljoin, quote

class EbcCrawler:
    def __init__(self, headless=True):
        self.session = requests.Session()
        # 실제 최신 브라우저와 똑같은 환경 설정
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://m.ebcblue.com/',
            'Connection': 'keep-alive'
        }

    def _init_driver(self): pass
    def close(self): pass

    def get_categorized_links(self, url, keyword=None, *args, **kwargs):
        # [핵심] 키워드가 있으면 검색 기능을 직접 사용하도록 URL 변환
        final_url = url
        if keyword:
            encoded_kw = quote(keyword.encode('utf-8'))
            sep = "&" if "?" in url else "?"
            final_url = f"{url}{sep}sfl=wr_subject||wr_content&stx={encoded_kw}"
        
        st.write(f"🔍 **접속 URL:** {final_url}")
        raw_links = self.get_post_links(final_url, keyword)
        return {'notice': [], 'normal': raw_links}

    def get_post_links(self, url, keyword=None):
        links = []
        try:
            # 첫 번째 접속으로 쿠키 획득
            self.session.get("https://m.ebcblue.com/", headers=self.headers, timeout=10)
            res = self.session.get(url, headers=self.headers, timeout=15)
            res.raise_for_status()
            
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # 모든 <a> 태그를 뒤져서 게시글 번호(wr_id)가 있는 것만 추출
            all_a = soup.find_all('a', href=True)
            for a in all_a:
                href = a['href']
                text = a.get_text(strip=True)
                
                # 그누보드 전용 게시글 링크 패턴
                if 'wr_id=' in href and 'bo_table=' in href:
                    # 쓰기, 삭제 등 불필요한 기능 제외
                    if any(x in href for x in ['write', 'update', 'delete', 'search']):
                        continue
                        
                    full_link = urljoin(url, href)
                    # 중복 제거 및 키워드 검증
                    if full_link not in links:
                        if not keyword or (keyword in text or keyword in full_link):
                            links.append(full_link)
            
            st.write(f"🎯 **발견된 실습 게시글:** {len(links)}개")
            return links
        except Exception as e:
            st.error(f"❌ 접속 중 오류 발생: {e}")
            return []

    def get_post_content(self, url):
        try:
            res = self.session.get(url, headers=self.headers)
            soup = BeautifulSoup(res.text, 'html.parser')
            title = soup.find('h1') or soup.find('h2') or soup.find('title')
            content = soup.find(id="bo_v_con") or soup.find(class_="view-content")
            return {
                'title': title.get_text(strip=True) if title else "제목 없음",
                'content': content.get_text(strip=True)[:1000] if content else "내용 없음",
                'date': '2026-01-30'
            }
        except: return {'title': "Error", 'content': "", 'date': ""}
"""

with open(target_file, "w", encoding="utf-8") as f:
    f.write(crawler_code)

print("✅ 최종 승리 패치가 적용되었습니다!")
