import requests
from bs4 import BeautifulSoup
import time
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
        print(f"🚀 [Target] {url} | Keyword: {keyword}")
        raw_links = self.get_post_links(url, keyword)
        return {'notice': [], 'normal': raw_links}

    def get_post_links(self, url, keyword=None):
        links = []
        try:
            res = self.session.get(url, headers=self.headers, timeout=10)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # <a> 태그 전체 탐색
            all_a_tags = soup.find_all('a', href=True)
            print(f"🔍 Found {len(all_a_tags)} total links on page.")

            for a in all_a_tags:
                href = a['href']
                text = a.get_text(strip=True)
                
                # 그누보드 모바일/PC 게시글 공통 패턴
                is_post = 'wr_id=' in href or 'board.php?bo_table=' in href
                is_junk = any(x in href for x in ['write', 'update', 'delete', 'token', 'admin', 'search'])
                
                if is_post and not is_junk:
                    full_link = urljoin(url, href)
                    
                    # 키워드 필터링 (키워드가 없으면 무조건 수집)
                    if not keyword:
                        if full_link not in links: links.append(full_link)
                    else:
                        # 제목이나 링크에 키워드가 포함되었는지 확인
                        if keyword in text or keyword in full_link:
                            if full_link not in links: links.append(full_link)
            
            # 중복 제거 및 최종 결과 보고
            unique_links = list(set(links))
            print(f"✅ Filtered {len(unique_links)} candidate links.")
            return unique_links

        except Exception as e:
            print(f"❌ Error: {e}")
            return []

    def get_post_content(self, url):
        try:
            res = self.session.get(url, headers=self.headers)
            soup = BeautifulSoup(res.text, 'html.parser')
            title = soup.find('h1') or soup.find('h2') or soup.find('title')
            content = soup.find(id="bo_v_con") or soup.find(class_="view-content") or soup.body
            return {
                'title': title.get_text(strip=True) if title else "No Title",
                'content': content.get_text(strip=True)[:500] if content else "No Content",
                'date': '2026-01-30'
            }
        except:
            return {'title': "Error", 'content': "", 'date': ""}
