import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin

class EbcCrawler:
    def __init__(self, headless=True):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
        }

    def _init_driver(self):
        pass

    def close(self):
        pass

    # [수정] 어떤 인자가 들어와도 에러 없이 다 받도록 수정 (*args, **kwargs 추가)
    def get_categorized_links(self, url, keyword=None, *args, **kwargs):
        print(f"🚀 [Stealth] Searching: {url} (Keyword: {keyword})")
        
        # 추가로 들어온 인자(예: 페이지 수)가 있다면 확인
        max_pages = args[0] if args else 1
        print(f"📄 Scan pages: {max_pages}")

        raw_links = self.get_post_links(url, keyword)
        return {
            'notice': [],
            'normal': raw_links
        }

    def get_post_links(self, url, keyword=None):
        links = []
        try:
            response = self.session.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for a in soup.find_all('a', href=True):
                href = a['href']
                if 'wr_id=' in href and 'bo_table=' in href:
                    if any(x in href for x in ['write', 'delete', 'update', 'reply']):
                        continue
                    full_link = urljoin(url, href)
                    if full_link not in links:
                        links.append(full_link)
            
            print(f"✅ Found {len(links)} posts.")
            return links
        except Exception as e:
            print(f"❌ Error: {e}")
            return []

    def get_post_content(self, url):
        try:
            res = self.session.get(url, headers=self.headers)
            soup = BeautifulSoup(res.text, 'html.parser')
            title = soup.title.string if soup.title else "No Title"
            content_div = soup.find(id="bo_v_con")
            content = content_div.get_text(strip=True) if content_div else "Content not found"
            return {'title': title, 'content': content, 'date': '2024-01-01'}
        except:
            return {'title': "Error", 'content': "", 'date': ""}
