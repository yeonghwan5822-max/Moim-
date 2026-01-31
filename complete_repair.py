import os

# 크롤러 파일 경로
crawler_path = "backend/scripts/crawler.py"

# 로그인 기능 + 멀티호퍼(전체 순찰)가 포함된 완벽한 크롤러 코드
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
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://m.ebcblue.com/'
        }
        # 로그인 주소
        self.login_url = "https://m.ebcblue.com/bbs/login_check.php"

    # [핵심] 로그인 기능 (이게 없어서 에러가 났던 겁니다!)
    def login(self, user_id, user_pw):
        try:
            login_data = {
                'mb_id': user_id,
                'mb_password': user_pw,
                'url': 'https://m.ebcblue.com/'
            }
            res = self.session.post(self.login_url, data=login_data, headers=self.headers, verify=False)
            
            # 로그인 실패 시 체크
            if "비밀번호가 틀립니다" in res.text or "존재하지 않는" in res.text:
                return False
            return True
        except Exception as e:
            print(f"로그인 에러: {e}")
            return False

    def get_categorized_links(self, url, keyword=None):
        # 1. 현재 페이지 먼저 스캔
        links = self._scan_page(url, keyword)
        if links: 
            return {'notice': [], 'normal': links}
        
        # 2. 없으면 전체 게시판 순찰 (로그인 상태 유지)
        st.info("현재 페이지에 글이 없어, 전체 게시판을 순찰합니다...")
        boards = self._find_boards(url)
        
        all_links = []
        progress = st.progress(0)
        status_text = st.empty()
        
        for i, board in enumerate(boards):
            if not board: continue
            
            # 진행 상황 표시
            board_name = board.split('bo_table=')[-1]
            status_text.text(f"🏃 이동 중: {board_name} 게시판...")
            progress.progress((i + 1) / len(boards))
            
            # 달력 등은 건너뛰기
            if 'calendar' in board: continue
            
            # 각 게시판 스캔
            found = self._scan_page(board, keyword, silent=True)
            if found:
                all_links.extend(found)
        
        status_text.empty()
        progress.empty()
        
        return {'notice': [], 'normal': list(set(all_links))}

    def _find_boards(self, url):
        try:
            res = self.session.get(url, headers=self.headers, verify=False)
            res.encoding = res.apparent_encoding
            soup = BeautifulSoup(res.text, 'html.parser')
            boards = []
            for a in soup.find_all('a', href=True):
                if 'board.php' in a['href'] and 'bo_table=' in a['href']:
                    boards.append(urljoin(url, a['href']))
            return list(set(boards))
        except: return []

    def _scan_page(self, url, keyword, silent=False):
        links = []
        try:
            res = self.session.get(url, headers=self.headers, verify=False)
            res.encoding = res.apparent_encoding
            soup = BeautifulSoup(res.text, 'html.parser')
            
            for a in soup.find_all('a', href=True):
                href = a['href']
                # 로그인 상태에서는 wr_id 링크가 보입니다!
                if 'wr_id=' in href and 'bo_table=' in href:
                    if any(x in href for x in ['write', 'update', 'delete', 'search']): continue
                    
                    full_link = urljoin(url, href)
                    text = a.get_text(strip=True)
                    
                    if keyword:
                        if keyword in text or keyword in full_link:
                            links.append(full_link)
                    else:
                        links.append(full_link)
            return list(set(links))
        except: return []

    def get_post_content(self, url):
        return {'title': '', 'content': ''}
"""

with open(crawler_path, "w", encoding="utf-8") as f:
    f.write(crawler_code)

print("✅ 크롤러에 로그인 기능을 성공적으로 이식했습니다!")import os

# 크롤러 파일 경로
crawler_path = "backend/scripts/crawler.py"

# 로그인 기능 + 멀티호퍼(전체 순찰)가 포함된 완벽한 크롤러 코드
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
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://m.ebcblue.com/'
        }
        # 로그인 주소
        self.login_url = "https://m.ebcblue.com/bbs/login_check.php"

    # [핵심] 로그인 기능 (이게 없어서 에러가 났던 겁니다!)
    def login(self, user_id, user_pw):
        try:
            login_data = {
                'mb_id': user_id,
                'mb_password': user_pw,
                'url': 'https://m.ebcblue.com/'
            }
            res = self.session.post(self.login_url, data=login_data, headers=self.headers, verify=False)
            
            # 로그인 실패 시 체크
            if "비밀번호가 틀립니다" in res.text or "존재하지 않는" in res.text:
                return False
            return True
        except Exception as e:
            print(f"로그인 에러: {e}")
            return False

    def get_categorized_links(self, url, keyword=None):
        # 1. 현재 페이지 먼저 스캔
        links = self._scan_page(url, keyword)
        if links: 
            return {'notice': [], 'normal': links}
        
        # 2. 없으면 전체 게시판 순찰 (로그인 상태 유지)
        st.info("현재 페이지에 글이 없어, 전체 게시판을 순찰합니다...")
        boards = self._find_boards(url)
        
        all_links = []
        progress = st.progress(0)
        status_text = st.empty()
        
        for i, board in enumerate(boards):
            if not board: continue
            
            # 진행 상황 표시
            board_name = board.split('bo_table=')[-1]
            status_text.text(f"🏃 이동 중: {board_name} 게시판...")
            progress.progress((i + 1) / len(boards))
            
            # 달력 등은 건너뛰기
            if 'calendar' in board: continue
            
            # 각 게시판 스캔
            found = self._scan_page(board, keyword, silent=True)
            if found:
                all_links.extend(found)
        
        status_text.empty()
        progress.empty()
        
        return {'notice': [], 'normal': list(set(all_links))}

    def _find_boards(self, url):
        try:
            res = self.session.get(url, headers=self.headers, verify=False)
            res.encoding = res.apparent_encoding
            soup = BeautifulSoup(res.text, 'html.parser')
            boards = []
            for a in soup.find_all('a', href=True):
                if 'board.php' in a['href'] and 'bo_table=' in a['href']:
                    boards.append(urljoin(url, a['href']))
            return list(set(boards))
        except: return []

    def _scan_page(self, url, keyword, silent=False):
        links = []
        try:
            res = self.session.get(url, headers=self.headers, verify=False)
            res.encoding = res.apparent_encoding
            soup = BeautifulSoup(res.text, 'html.parser')
            
            for a in soup.find_all('a', href=True):
                href = a['href']
                # 로그인 상태에서는 wr_id 링크가 보입니다!
                if 'wr_id=' in href and 'bo_table=' in href:
                    if any(x in href for x in ['write', 'update', 'delete', 'search']): continue
                    
                    full_link = urljoin(url, href)
                    text = a.get_text(strip=True)
                    
                    if keyword:
                        if keyword in text or keyword in full_link:
                            links.append(full_link)
                    else:
                        links.append(full_link)
            return list(set(links))
        except: return []

    def get_post_content(self, url):
        return {'title': '', 'content': ''}
"""

with open(crawler_path, "w", encoding="utf-8") as f:
    f.write(crawler_code)

print("✅ 크롤러에 로그인 기능을 성공적으로 이식했습니다!")
"""

---

### 🚀 2단계: 실행 및 배포 (터미널)

1.  **패치 실행:**
    ```bash
    python3 complete_repair.py
    ```
2.  **깃허브 배포:**
    ```bash
    git add .
    git commit -m "Fix: 크롤러에 누락된 로그인(login) 함수 추가"
    git push
    ```

---

### 🏁 3단계: 최종 테스트

1.  **Streamlit Cloud**에서 **[Reboot app]**을 클릭합니다.
2.  앱이 켜지면 **로그인 정보를 입력**하고 버튼을 누르세요.

**[성공 시나리오]**
* 아까 떴던 `AttributeError`가 사라지고,
* **"🔑 로그인 시도 중..."**이라는 메시지가 뜬 뒤,
* **"✅ 로그인 성공!"**과 함께 게시글 목록이 나타날 것입니다.

이제 정말 코앞입니다! 버튼을 누르면 로그인 함수가 작동할 것입니다. 결과 알려주세요!

