import os

target_file = "backend/scripts/crawler.py"

crawler_code = """import requests
from bs4 import BeautifulSoup
import streamlit as st
from urllib.parse import urljoin, quote
import urllib3
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class EbcCrawler:
    def __init__(self, headless=True):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
            'Referer': 'https://m.ebcblue.com/'
        }

    def _init_driver(self): pass
    def close(self): pass

    def get_categorized_links(self, url, keyword=None, *args, **kwargs):
        # 1. 일단 검색 쿼리 없이 전체 목록에 먼저 접속합니다 (차단 방지)
        st.info(f"🌐 게시판 접속 중: {url}")
        raw_links = self.get_post_links(url, keyword)
        return {'notice': [], 'normal': raw_links}

    def get_post_links(self, url, keyword=None):
        links = []
        try:
            # SSL 우회하여 데이터 가져오기
            res = self.session.get(url, headers=self.headers, verify=False, timeout=15)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # [특수 로직] 모든 <a> 태그를 대상으로 매우 넓은 범위의 탐색 실시
            all_a = soup.find_all('a', href=True)
            st.write(f"🔍 전체 탐색된 링크 수: {len(all_a)}개")

            for a in all_a:
                href = a['href']
                text = a.get_text(strip=True)
                
                # 게시글 번호가 포함된 모든 링크 패턴 (wr_id)
                if 'wr_id=' in href:
                    # 관리용 링크 제외
                    if any(x in href for x in ['write', 'update', 'delete', 'search']):
                        continue
                    
                    full_link = urljoin(url, href)
                    
                    # 키워드 '실습'이 제목이나 링크에 포함되어 있는지 확인
                    if not keyword or (keyword in text or keyword in full_link):
                        if full_link not in links:
                            links.append(full_link)
            
            # 만약 검색 결과가 없다면, 그누보드 검색 파라미터를 강제로 붙여서 재시도
            if not links and keyword:
                st.warning("⚠️ 일반 목록에서 못 찾았습니다. 검색 모드로 전환합니다.")
                encoded_kw = quote(keyword.encode('utf-8'))
                search_url = f"{url}&sfl=wr_subject||wr_content&stx={encoded_kw}"
                return self.get_post_links(search_url, None) # 재귀 호출

            st.success(f"🎯 최종 발견된 게시물: {len(links)}개")
            return links
        except Exception as e:
            st.error(f"❌ 데이터 수집 중 오류: {e}")
            return []

    def get_post_content(self, url):
        try:
            res = self.session.get(url, headers=self.headers, verify=False, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')
            title = soup.find(['h1', 'h2', 'title'])
            content = soup.find(id="bo_v_con") or soup.find(class_="view-content") or soup.body
            return {
                'title': title.get_text(strip=True) if title else "제목 없음",
                'content': content.get_text(strip=True)[:2000] if content else "본문 없음",
                'date': '2026-01-30'
            }
        except: return {'title': 'Error', 'content': '', 'date': ''}
"""

with open(target_file, "w", encoding="utf-8") as f:
    f.write(crawler_code)

print("✅ 초정밀 저인망 크롤러로 교체 완료!")
