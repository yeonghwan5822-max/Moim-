import requests
from bs4 import BeautifulSoup
import time
import streamlit as st
from urllib.parse import urljoin

class EbcCrawler:
    def __init__(self, headless=True):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'
        }

    def _init_driver(self): pass
    def close(self): pass

    def get_categorized_links(self, url, keyword=None, *args, **kwargs):
        # [진단] 앱 화면에 현재 상태를 출력합니다.
        st.write(f"🔍 **접속 시도:** {url}")
        raw_links = self.get_post_links(url, keyword)
        return {'notice': [], 'normal': raw_links}

    def get_post_links(self, url, keyword=None):
        links = []
        try:
            res = self.session.get(url, headers=self.headers, timeout=10)
            
            # [진단] HTTP 상태 코드 확인
            if res.status_code == 200:
                st.success(f"✅ 서버 응답 성공 (200)")
            else:
                st.error(f"❌ 서버 응답 실패 (상태 코드: {res.status_code})")
                return []

            soup = BeautifulSoup(res.text, 'html.parser')
            
            # [진단] 페이지 제목 확인
            title = soup.title.string if soup.title else "제목 없음"
            st.write(f"📄 **페이지 제목:** {title}")

            # 모든 <a> 태그 탐색 (더 공격적인 추출)
            all_a = soup.find_all('a', href=True)
            st.write(f"🔗 **페이지 내 총 링크 수:** {len(all_a)}개")

            for a in all_a:
                href = a['href']
                text = a.get_text(strip=True)
                
                # 게시글로 추정되는 모든 패턴 수집
                is_post = any(p in href for p in ['wr_id=', 'bo_table=', 'board.php'])
                is_junk = any(j in href for j in ['write', 'update', 'delete', 'token', 'search'])
                
                if is_post and not is_junk:
                    full_link = urljoin(url, href)
                    if not keyword or (keyword in text or keyword in full_link):
                        if full_link not in links:
                            links.append(full_link)
            
            st.write(f"🎯 **최종 추출된 게시글:** {len(links)}개")
            return links

        except Exception as e:
            st.error(f"❌ 크롤링 중 에러 발생: {e}")
            return []

    def get_post_content(self, url):
        return {'title': 'Test', 'content': 'Test Content', 'date': '2026-01-30'}
