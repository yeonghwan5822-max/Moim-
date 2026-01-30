import os

# 크롤러 코드 (crawler.py) - 노필터(No-Filter) 모드
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
        st.info(f"🔍 [노필터 모드] 접속 URL: {url}")
        links = self.get_post_links(url, keyword)
        return {'notice': [], 'normal': links}

    def get_post_links(self, url, keyword=None):
        links = []
        try:
            res = self.session.get(url, headers=self.headers, verify=False, timeout=15)
            res.encoding = res.apparent_encoding
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # 페이지에 있는 모든 <a> 태그 수집
            all_a = soup.find_all('a', href=True)
            
            # [진단] 실제 링크 모양을 화면에 찍어봅니다 (상위 10개)
            with st.expander("👀 크롤러가 보고 있는 실제 링크들 (여기를 눌러 확인)", expanded=True):
                st.write(f"총 발견된 링크 수: {len(all_a)}개")
                sample_links = []
                for a in all_a[:10]:
                    sample_links.append(f"[{a.get_text(strip=True)}] -> {a['href']}")
                st.code("\\n".join(sample_links))

            # [수집 로직 대폭 완화]
            for a in all_a:
                href = a['href']
                text = a.get_text(strip=True)
                full_link = urljoin(url, href)
                
                # 조건: 그냥 '글쓰기(write)', '검색(search)' 같은 게 아니면 다 가져옵니다.
                # wr_id나 bo_table 검사를 뺐습니다.
                is_junk = any(x in href for x in ['write', 'update', 'delete', 'search', 'login', 'logout', 'password'])
                
                if not is_junk:
                    # 링크 길이가 너무 짧으면(메인화면 이동 등) 제외
                    if len(href) > 3:
                         # 키워드 필터링 (키워드가 있으면 검사)
                        if keyword:
                            if keyword.lower() in text.lower() or keyword.lower() in full_link.lower():
                                if full_link not in links: links.append(full_link)
                        else:
                            # 키워드 없으면 무조건 수집
                            if full_link not in links: links.append(full_link)
            
            if links:
                st.success(f"🎯 필터 해제 후 {len(links)}개의 링크를 건졌습니다!")
            else:
                st.error("❌ 필터를 다 껐는데도 링크가 없습니다. 위 '실제 링크들'을 확인해주세요.")
                
            return links

        except Exception as e:
            st.error(f"❌ 오류: {e}")
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

with open("backend/scripts/crawler.py", "w", encoding="utf-8") as f:
    f.write(crawler_code)

print("✅ 노필터(No-Filter) 진단 모드 설치 완료!")
