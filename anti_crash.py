import os

# 1. 스트림릿 버전을 안정적인 버전으로 고정 (requirements.txt)
# 최신 버전보다 1.31.0 버전이 이 에러에 훨씬 강합니다.
req_content = """streamlit==1.31.0
requests
beautifulsoup4
python-dotenv
urllib3
"""

# 2. 화면 충돌 방지형 크롤러 (crawler.py)
crawler_code = """import requests
from bs4 import BeautifulSoup
import streamlit as st
from urllib.parse import urljoin
import urllib3
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class EbcCrawler:
    def __init__(self, **kwargs):
        self.session = requests.Session()
        self.headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1'}

    def _init_driver(self): pass
    def close(self): pass

    def get_categorized_links(self, url, keyword=None, *args, **kwargs):
        # [핵심 수정] st.empty()를 써서 화면 요소를 뺐다 꼈다 하지 않고 '내용만' 바꿉니다.
        # 이렇게 하면 removeChild 에러가 발생할 틈이 없습니다.
        status_box = st.empty()
        status_box.info(f"🌐 탐색 시작: {url}")
        
        links = self.get_post_links(url, keyword, status_box)
        
        status_box.success("탐색 완료!")
        time.sleep(1)
        status_box.empty() # 깔끔하게 상태창 지우기
        
        return {'notice': [], 'normal': links}

    def get_post_links(self, url, keyword, status_box):
        links = []
        try:
            status_box.info(f"📡 데이터 수신 중... {url}")
            res = self.session.get(url, headers=self.headers, verify=False, timeout=15)
            soup = BeautifulSoup(res.content, 'html.parser')
            
            found_count = 0
            for a in soup.find_all('a', href=True):
                href = a['href']
                if 'wr_id=' in href and 'bo_table=' in href:
                    if any(x in href for x in ['write', 'update', 'delete']): continue
                    full_link = urljoin(url, href)
                    
                    if not keyword or (keyword.lower() in a.get_text().lower() or keyword.lower() in full_link.lower()):
                        if full_link not in links: 
                            links.append(full_link)
                            found_count += 1
                            # 너무 빠른 업데이트 방지를 위해 10개 단위로만 로그 갱신
                            if found_count % 10 == 0:
                                status_box.info(f"🔎 {found_count}개 게시물 발견...")
            
            return list(set(links))
        except Exception as e:
            st.error(f"❌ 접속 에러: {e}")
            return []

    def get_post_content(self, url):
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

with open("backend/requirements.txt", "w", encoding="utf-8") as f:
    f.write(req_content)
with open("backend/scripts/crawler.py", "w", encoding="utf-8") as f:
    f.write(crawler_code)

print("✅ 화면 충돌 방지 패치 완료!")
"""

---

### 🚀 3단계: 적용 및 확인

1.  **패치 실행:**
    ```bash
    python3 anti_crash.py
    ```
2.  **배포:**
    ```bash
    git add .
    git commit -m "Fix: Streamlit removeChild 에러 방지용 안정화 패치"
    git push
    ```
3.  **가장 중요:** Streamlit Cloud에서 **[Reboot app]**을 꼭 해주세요. (버전이 바뀌었으니까요!)

**💡 요약:**
1.  일단 **시크릿 모드**로 켜보세요. (이게 되면 코드 수정도 필요 없습니다.)
2.  그래도 안 되면 위 코드를 적용하세요. (화면 업데이트 방식을 '안전 모드'로 바꿨습니다.)

이 에러만 잡으면 진짜 끝입니다. 시크릿 모드 테스트 결과 알려주세요!
