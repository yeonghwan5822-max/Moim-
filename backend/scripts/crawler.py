import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin, urlparse

class EbcCrawler:
    def __init__(self, headless=True):
        self.session = requests.Session()
        # 브라우저인 척 위장력을 높였습니다.
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'
        }

    def _init_driver(self): pass
    def close(self): pass

    def get_categorized_links(self, url, keyword=None, *args, **kwargs):
        print(f"🚀 [Target] {url}")
        raw_links = self.get_post_links(url, keyword)
        return {'notice': [], 'normal': raw_links}

    def get_post_links(self, url, keyword=None):
        links = []
        try:
            res = self.session.get(url, headers=self.headers, timeout=10)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # 모든 <a> 태그를 다 뒤집니다.
            for a in soup.find_all('a', href=True):
                href = a['href']
                # 그누보드 핵심 패턴: wr_id 또는 bo_table이 들어간 모든 링크
                if 'wr_id=' in href or 'bo_table=' in href:
                    # 쓰기, 수정, 관리자 기능 등 불필요한 링크 제외
                    if any(x in href for x in ['write', 'update', 'delete', 'token', 'admin']):
                        continue
                    
                    full_link = urljoin(url, href)
                    
                    # 키워드가 있다면 제목이나 링크에 포함된 경우만 수집
                    if keyword:
                        if keyword in a.get_text() or keyword in full_link:
                            if full_link not in links: links.append(full_link)
                    else:
                        if full_link not in links: links.append(full_link)
            
            # 만약 아무것도 못 찾았다면? 더 넓은 범위로 한 번 더 시도
            if not links:
                print("⚠️ No standard patterns found. Trying broad search...")
                for a in soup.find_all('a', href=True):
                    if '/bbs/board.php' in a['href'] and 'wr_id' in a['href']:
                        full_link = urljoin(url, a['href'])
                        if full_link not in links: links.append(full_link)

            print(f"✅ Found {len(links)} candidate links.")
            return links

        except Exception as e:
            print(f"❌ Fetch Error: {e}")
            return []

    def get_post_content(self, url):
        try:
            res = self.session.get(url, headers=self.headers)
            soup = BeautifulSoup(res.text, 'html.parser')
            title = soup.find('h1') or soup.find('h2') or soup.title
            title_text = title.get_text(strip=True) if title else "No Title"
            
            # 본문 영역 탐색 (GnuBoard 표준 ID들)
            content_div = soup.find(id="bo_v_con") or soup.find(class_="view-content") or soup.body
            content_text = content_div.get_text(strip=True)[:500] if content_div else "No Content"
            
            return {'title': title_text, 'content': content_text, 'date': '2026-01-30'}
        except:
            return {'title': "Error", 'content': "", 'date': ""}
