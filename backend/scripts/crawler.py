import requests
from bs4 import BeautifulSoup
import time

class EbcCrawler:
    def __init__(self, headless=True):
        # 브라우저 대신 '세션'을 사용 (로그인 유지 등 가능)
        self.session = requests.Session()
        # 사람인 척 위장하는 가면 (User-Agent)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def _init_driver(self):
        # 브라우저를 안 쓰니 초기화할 게 없음
        pass

    def close(self):
        pass

    def get_post_links(self, url, keyword=None):
        print(f"🚀 Fetching URL (Stealth Mode): {url}")
        try:
            # 1. 웹페이지 요청 (브라우저 없이 접속)
            response = self.session.get(url, headers=self.headers)
            response.raise_for_status() # 에러 체크
            
            # 2. HTML 해석
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string if soup.title else 'No Title'
            print(f"✅ 접속 성공! 페이지 제목: {title}")
            
            # 3. 링크 찾기 (그누보드 패턴: wr_id)
            links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                # 게시글 링크 패턴이 보이면 수집
                if 'wr_id=' in href and 'bo_table=' in href:
                    full_link = href if href.startswith('http') else url + href
                    links.append(full_link)
            
            print(f"Found {len(links)} links.")
            return links

        except Exception as e:
            print(f"❌ Error: {e}")
            return []
