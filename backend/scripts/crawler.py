import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin

class EbcCrawler:
    def __init__(self, headless=True):
        # 브라우저 없이 가벼운 'Requests' 사용
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
        }

    def _init_driver(self):
        pass # 브라우저 안 쓰니까 패스

    def close(self):
        pass # 닫을 브라우저 없음

    def login(self):
        pass # 필요하면 나중에 구현

    # [핵심] 아까 에러났던 그 함수! (이름 추가됨)
    def get_categorized_links(self, url, keyword=None):
        print(f"🚀 [Stealth] Searching: {url}")
        
        # 1. 링크 수집
        raw_links = self.get_post_links(url, keyword)
        
        # 2. 분류 (일단 'normal'에 다 몰아넣기 -> 에러 방지)
        return {
            'notice': [],
            'normal': raw_links
        }

    # 실제 링크 찾는 로직
    def get_post_links(self, url, keyword=None):
        links = []
        try:
            response = self.session.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 그누보드 게시글 패턴 (wr_id가 있는 링크 찾기)
            for a in soup.find_all('a', href=True):
                href = a['href']
                if 'wr_id=' in href and 'bo_table=' in href:
                    # '글쓰기', '답변', '삭제' 같은 기능 링크 제외
                    if 'write' in href or 'delete' in href or 'update' in href:
                        continue
                        
                    # 절대 경로로 변환
                    full_link = urljoin(url, href)
                    if full_link not in links:
                        links.append(full_link)
            
            print(f"✅ Found {len(links)} posts.")
            return links

        except Exception as e:
            print(f"❌ Error fetching links: {e}")
            return []

    # 내용 가져오기 (혹시 몰라 미리 추가)
    def get_post_content(self, url):
        try:
            res = self.session.get(url, headers=self.headers)
            soup = BeautifulSoup(res.text, 'html.parser')
            title = soup.title.string if soup.title else "No Title"
            # 본문 대충 긁어오기 (id="bo_v_con" 등 그누보드 표준)
            content_div = soup.find(id="bo_v_con")
            content = content_div.get_text(strip=True) if content_div else "Content not found"
            return {'title': title, 'content': content, 'date': '2024-01-01'}
        except:
            return {'title': "Error", 'content': "", 'date': ""}
