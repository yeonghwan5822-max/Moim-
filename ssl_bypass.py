import os

target_file = "backend/scripts/crawler.py"

crawler_code = """import requests
from bs4 import BeautifulSoup
import time
import streamlit as st
from urllib.parse import urljoin, quote
import urllib3

# [핵심] SSL 경고 메시지 끄기
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class EbcCrawler:
    def __init__(self, headless=True):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }

    def _init_driver(self): pass
    def close(self): pass

    def get_categorized_links(self, url, keyword=None, *args, **kwargs):
        # 검색 URL 생성 로직
        final_url = url
        if keyword:
            encoded_kw = quote(keyword.encode('utf-8'))
            sep = "&" if "?" in url else "?"
            final_url = f"{url}{sep}sfl=wr_subject||wr_content&stx={encoded_kw}"
        
        st.write(f"🌐 **접속 시도 (SSL 우회):** {final_url}")
        raw_links = self.get_post_links(final_url, keyword)
        return {'notice': [], 'normal': raw_links}

    def get_post_links(self, url, keyword=None):
        links = []
        try:
            # [핵심] verify=False 를 추가하여 SSL 인증서 검사를 건너뜁니다.
            res = self.session.get(url, headers=self.headers, timeout=15, verify=False)
            res.raise_for_status()
            
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # 더 정밀한 링크 추출 (그누보드 모바일 게시판용)
            all_a = soup.find_all('a', href=True)
            for a in all_a:
                href = a['href']
                text = a.get_text(strip=True)
                
                # wr_id가 포함된 실제 게시글 링크만 필터링
                if 'wr_id=' in href:
                    if any(x in href for x in ['write', 'update', 'delete']): continue
                    
                    full_link = urljoin(url, href)
                    if full_link not in links:
                        # 키워드가 있다면 제목/링크 대조
                        if not keyword or (keyword in text or keyword in full_link):
                            links.append(full_link)
            
            st.success(f"🎯 **'{keyword if keyword else '전체'}'** 검색 결과: {len(links)}개 발견")
            return links
        except Exception as e:
            st.error(f"❌ 접속 실패: {e}")
            return []

    def get_post_content(self, url):
        try:
            res = self.session.get(url, headers=self.headers, verify=False, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')
            title = soup.find('h1') or soup.find('h2') or soup.find('title')
            content = soup.find(id="bo_v_con") or soup.find(class_="view-content")
            return {
                'title': title.get_text(strip=True) if title else "제목 없음",
                'content': content.get_text(strip=True)[:1500] if content else "본문 없음",
                'date': '2026-01-30'
            }
        except: return {'title': 'Error', 'content': '', 'date': ''}
"""

with open(target_file, "w", encoding="utf-8") as f:
    f.write(crawler_code)

print("✅ SSL 우회 패치 완료!")

