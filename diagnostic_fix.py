import os

# 크롤러 코드 (crawler.py) - HTML 구조 진단 및 강제 추출 모드
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
        st.info(f"📡 분석 시작: {url}")
        links = self.get_post_links(url, keyword)
        return {'notice': [], 'normal': links}

    def get_post_links(self, url, keyword=None):
        links = []
        try:
            res = self.session.get(url, headers=self.headers, verify=False, timeout=15)
            res.encoding = res.apparent_encoding
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # [진단 리포트] 사이트가 로그인 페이지인지, 빈 페이지인지 확인
            with st.expander("🔍 사이트 내부 투시경 (여기를 클릭하세요!)", expanded=True):
                st.write(f"**응답 코드:** {res.status_code}")
                st.write(f"**페이지 제목:** {soup.title.string if soup.title else '제목 없음'}")
                
                # 페이지에 있는 모든 링크를 싹 다 긁어봅니다.
                all_tags = soup.find_all('a', href=True)
                st.write(f"**발견된 총 링크 수:** {len(all_tags)}개")
                
                # 링크 샘플 5개 출력
                if all_tags:
                    st.write("🔗 **링크 샘플 (상위 5개):**")
                    for i, tag in enumerate(all_tags[:5]):
                        st.code(f"{tag.get_text(strip=True)} -> {tag['href']}")

            # [강제 추출] wr_id 조건이 안 맞으면 'board.php'가 들어간 모든 링크를 수집
            for a in soup.find_all('a', href=True):
                href = a['href']
                text = a.get_text(strip=True)
                full_link = urljoin(url, href)

                # 조건 1: wr_id가 있는 정석 게시글
                if 'wr_id=' in href:
                     if not any(x in href for x in ['write', 'update', 'delete', 'search']):
                        if self._check_keyword(keyword, text, full_link):
                            if full_link not in links: links.append(full_link)
                
                # 조건 2 (비상용): wr_id는 없지만 게시판 링크처럼 생긴 것
                elif 'board.php' in href and 'bo_table' in href:
                     if self._check_keyword(keyword, text, full_link):
                        if full_link not in links: links.append(full_link)

            if not links:
                st.error("⚠️ 게시글로 추정되는 링크를 하나도 못 건졌습니다. 위 '투시경' 내용을 확인해주세요.")
            else:
                st.success(f"🎯 {len(links)}개의 게시글 확보 성공!")
                
            return links

        except Exception as e:
            st.error(f"❌ 접속 에러: {e}")
            return []

    def _check_keyword(self, keyword, text, link):
        if not keyword: return True
        return (keyword.lower() in text.lower() or keyword.lower() in link.lower())

    def get_post_content(self, url):
        # 본문 추출 로직은 동일
        try:
            res = self.session.get(url, headers=self.headers, verify=False, timeout=10)
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

print("✅ 진단용 투시경 크롤러 설치 완료!")
