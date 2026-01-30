import os

# 크롤러 코드 (crawler.py) - 저인망식 추출 + 한글 깨짐 방지
crawler_code = """import requests
from bs4 import BeautifulSoup
import streamlit as st
from urllib.parse import urljoin
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class EbcCrawler:
    def __init__(self, **kwargs):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1'
        }

    def _init_driver(self): pass
    def close(self): pass

    def get_categorized_links(self, url, keyword=None, *args, **kwargs):
        # 화면에 진행 상황 표시
        status = st.empty()
        status.info(f"📡 사이트 접속 중: {url}")
        
        links = self.get_post_links(url, keyword)
        
        status.empty() # 완료되면 상태창 지움
        return {'notice': [], 'normal': links}

    def get_post_links(self, url, keyword=None):
        links = []
        try:
            res = self.session.get(url, headers=self.headers, verify=False, timeout=15)
            # [핵심] 한글 깨짐 방지 (GnuBoard 특성)
            res.encoding = res.apparent_encoding 
            
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # 진단용 로그 (확장 메뉴로 숨김)
            with st.expander("🕵️‍♂️ 크롤링 상세 진단 로그 (클릭하여 열기)"):
                st.write(f"접속 상태 코드: {res.status_code}")
                all_a = soup.find_all('a', href=True)
                st.write(f"페이지 내 총 링크 수: {len(all_a)}개")
                
                match_count = 0
                for a in all_a:
                    href = a['href']
                    text = a.get_text(strip=True)
                    
                    # [조건 완화] bo_table 확인 제거, wr_id만 있으면 게시글로 간주
                    if 'wr_id=' in href:
                        # 관리자/시스템 링크 제외
                        if any(x in href for x in ['write', 'update', 'delete', 'search', 'login']):
                            continue
                            
                        full_link = urljoin(url, href)
                        
                        # 키워드 검사
                        is_match = False
                        if not keyword:
                            is_match = True
                        elif keyword.lower() in text.lower() or keyword.lower() in full_link.lower():
                            is_match = True
                        
                        if is_match:
                            if full_link not in links:
                                links.append(full_link)
                                match_count += 1
                                # 로그에 찾은 것 표시
                                st.write(f"✅ 발견: [{text}] -> {full_link}")
            
            if len(links) == 0:
                st.warning("⚠️ 게시글 링크 패턴(wr_id)을 찾지 못했습니다. 게시판 URL이 맞는지 확인해주세요.")
            else:
                st.success(f"🎯 총 {len(links)}개의 게시물을 확보했습니다.")
                
            return links

        except Exception as e:
            st.error(f"❌ 접속 오류: {e}")
            return []

    def get_post_content(self, url):
        try:
            res = self.session.get(url, headers=self.headers, verify=False, timeout=10)
            res.encoding = res.apparent_encoding
            soup = BeautifulSoup(res.text, 'html.parser')
            
            title = soup.find(['h1', 'h2', 'h3', 'title'])
            # 모바일 그누보드 본문 ID (bo_v_con)
            content = soup.find(id="bo_v_con") or soup.find(class_="view-content") or soup.body
            
            return {
                'title': title.get_text(strip=True) if title else "제목 없음",
                'content': content.get_text(strip=True) if content else "본문 없음",
                'date': '2026-01-31'
            }
        except: return {'title': 'Error', 'content': '', 'date': ''}
"""

with open("backend/scripts/crawler.py", "w", encoding="utf-8") as f:
    f.write(crawler_code)

print("✅ 초정밀 크롤러(한글 패치 포함) 설치 완료!")
