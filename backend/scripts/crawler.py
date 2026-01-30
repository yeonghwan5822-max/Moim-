import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin, quote

class EbcCrawler:
    def __init__(self, headless=True):
        self.session = requests.Session()
        # 실제 최신 아이폰 브라우저인 것처럼 더 정교하게 위장합니다.
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://m.ebcblue.com/'
        }

    def _init_driver(self): pass
    def close(self): pass

    def get_categorized_links(self, url, keyword=None, *args, **kwargs):
        # [핵심 로직] 키워드가 있으면 게시판의 '검색 URL'로 즉시 우회합니다.
        search_url = url
        if keyword:
            # 그누보드 표준 검색 파라미터 적용 (제목+내용 검색)
            clean_keyword = quote(keyword.encode('utf-8'))
            if '?' in url:
                search_url = f"{url}&sfl=wr_subject||wr_content&stx={clean_keyword}"
            else:
                search_url = f"{url}?sfl=wr_subject||wr_content&stx={clean_keyword}"
        
        print(f"🎯 검색 우회 접속: {search_url}")
        raw_links = self.get_post_links(search_url, keyword)
        return {'notice': [], 'normal': raw_links}

    def get_post_links(self, url, keyword=None):
        links = []
        try:
            # 사이트 접속 (쿠키 생성을 위해 세션 유지)
            res = self.session.get(url, headers=self.headers, timeout=15)
            res.raise_for_status()
            
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # 모든 <a> 태그에서 게시글 번호(wr_id)가 포함된 링크만 정밀 추출
            for a in soup.find_all('a', href=True):
                href = a['href']
                # 게시글 상세 페이지 패턴만 수집
                if 'wr_id=' in href and 'bo_table=' in href:
                    # 쓰기, 검색, 관리자 기능 등 제외
                    if any(x in href for x in ['write', 'search', 'admin', 'update', 'delete']):
                        continue
                        
                    full_link = urljoin(url, href)
                    if full_link not in links:
                        links.append(full_link)
            
            print(f"✅ 발견된 게시글: {len(links)}개")
            return links

        except Exception as e:
            print(f"❌ 크롤링 에러: {e}")
            return []

    def get_post_content(self, url):
        try:
            res = self.session.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')
            # 제목 추출 (모바일 버전 대응)
            title = soup.find('h1') or soup.find('h2') or soup.find('title')
            # 본문 추출 (그누보드 표준 ID)
            content = soup.find(id="bo_v_con") or soup.find(class_="view-content")
            
            return {
                'title': title.get_text(strip=True) if title else "제목 없음",
                'content': content.get_text(strip=True)[:1000] if content else "본문을 가져올 수 없습니다.",
                'date': '2026-01-30'
            }
        except:
            return {'title': "에러", 'content': "", 'date': ""}
