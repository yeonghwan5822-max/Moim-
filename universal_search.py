import os

# 1. 경로 보장
os.makedirs("backend/scripts", exist_ok=True)

# 2. 범용 크롤러 엔진 (어떤 키워드든 대응 가능)
crawler_code = """import requests
from bs4 import BeautifulSoup
import streamlit as st
from urllib.parse import urljoin
import urllib3

# 보안 인증서 오류 무시 설정
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
        \"\"\"사용자가 입력한 keyword를 기반으로 필터링을 수행합니다.\"\"\"
        search_msg = f"'{keyword}' 키워드로 검색 중..." if keyword else "전체 게시글 수집 중..."
        st.info(f"🌐 {search_msg} | 대상: {url}")
        
        raw_links = self.get_post_links(url, keyword)
        return {'notice': [], 'normal': raw_links}

    def get_post_links(self, url, keyword=None):
        links = []
        try:
            # SSL 우회(verify=False) 및 접속
            res = self.session.get(url, headers=self.headers, verify=False, timeout=15)
            res.raise_for_status()
            soup = BeautifulSoup(res.content, 'html.parser')
            
            # 페이지 내 모든 <a> 태그를 뒤져서 게시글 패턴 추출
            for a in soup.find_all('a', href=True):
                href = a['href']
                text = a.get_text(strip=True)
                
                # 그누보드 게시글 표준 패턴(wr_id)
                if 'wr_id=' in href and 'bo_table=' in href:
                    if any(x in href for x in ['write', 'update', 'delete', 'search']): 
                        continue
                    
                    full_link = urljoin(url, href)
                    
                    # [핵심] 범용 키워드 매칭 로직
                    # 키워드가 없으면 전부 수집, 있으면 제목이나 링크에 포함된 것만 수집
                    if not keyword:
                        if full_link not in links: links.append(full_link)
                    else:
                        # 대소문자 구분 없이 매칭 (영어 키워드 대비)
                        if keyword.lower() in text.lower() or keyword.lower() in full_link.lower():
                            if full_link not in links: links.append(full_link)
            
            if links:
                st.success(f"🎯 검색 결과: {len(links)}개의 게시물을 찾았습니다!")
            else:
                st.warning("⚠️ 해당 키워드를 포함한 게시물을 찾지 못했습니다.")
                
            return list(set(links))
        except Exception as e:
            st.error(f"❌ 접속 중 오류 발생: {e}")
            return []

    def get_post_content(self, url):
        \"\"\"게시글 본문을 긁어오는 기능\"\"\"
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

with open("backend/scripts/crawler.py", "w", encoding="utf-8") as f:
    f.write(crawler_code)

# 3. 환경 파일 최신화
with open("backend/requirements.txt", "w", encoding="utf-8") as f:
    f.write("streamlit\\nrequests\\nbeautifulsoup4\\ndeepl\\npython-dotenv\\nchromadb\\nsoynlp\\nurllib3")

print("💎 [Anti-Gravity] 범용 검색 엔진으로 업그레이드 완료!")
