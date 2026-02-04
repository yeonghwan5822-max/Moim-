
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import re
from datetime import datetime
import urllib3
from urllib.parse import urljoin

# SSL 경고 무시
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class PureCollector:
    def __init__(self, phpsessid: str):
        self.session = requests.Session()
        self.session.cookies.set('PHPSESSID', phpsessid, domain='m.ebcblue.com')
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://m.ebcblue.com/',
        }
        self.school_keywords = ['중도', '학식', '과잠', '팀플']
        self.raw_data = []

    def clean_text(self, text: str) -> str:
        """HTML 태그 제거 및 불필요한 공백 정리"""
        text = re.sub(r'\s+', ' ', text).strip()
        # 내비게이션 노이즈 제거 (예시)
        noise_patterns = [r'목록', r'쪽지', r'댓글', r'이전글', r'상단으로']
        for p in noise_patterns:
            text = text.replace(p, '')
        return text

    def smart_chunking(self, text: str, max_length=1000) -> list:
        """1000자 초과 시 문장 단위로 분할"""
        if len(text) <= max_length:
            return [text]

        chunks = []
        current_chunk = ""
        # 문장 종결 부호 뒤에서 분할
        sentences = re.split(r'(?<=[.?\n])', text)
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) > max_length:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence
            else:
                current_chunk += sentence
        
        if current_chunk:
            chunks.append(current_chunk)
        return chunks

    def extract_tags(self, text: str) -> str:
        """본문에서 학교 관련 키워드 추출"""
        found = [kw for kw in self.school_keywords if kw in text]
        return ",".join(found) if found else ""

    def get_board_links(self, board_url: str, pages: int = 1) -> list:
        """게시판의 여러 페이지를 순회하며 링크 수집"""
        all_links = []
        base_url = board_url.split('?')[0] # Remove params for cleanliness if needed, but board.php needs params
        
        for page in range(1, pages + 1):
            target = f"{board_url}&page={page}"
            print(f"📡 {page}페이지 수집 중... ({target})")
            
            try:
                res = self.session.get(target, headers=self.headers, verify=False, timeout=10)
                res.encoding = res.apparent_encoding
                soup = BeautifulSoup(res.text, 'html.parser')
                
                found_on_page = 0
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if 'wr_id=' in href and 'bo_table=' in href:
                        if any(x in href for x in ['write', 'update', 'delete', 'search', 'login']): continue
                        
                        full_link = urljoin(board_url, href)
                        if full_link not in all_links:
                            all_links.append(full_link)
                            found_on_page += 1
                
                print(f"   -> {found_on_page}개 글 발견")
                time.sleep(1) # 부하 방지
            except Exception as e:
                print(f"❌ {page}페이지 접속 오류: {e}")
        
        return list(set(all_links)) # 최종 중복 제거

    def process_post(self, url: str, keyword: str = None):
        """개별 게시글 상세 수집 및 저장 (keyword 필터링 추가)"""
        try:
            res = self.session.get(url, headers=self.headers, verify=False, timeout=10)
            res.encoding = res.apparent_encoding
            soup = BeautifulSoup(res.text, 'html.parser')

            # 메타데이터 추출
            post_id = re.search(r'wr_id=(\d+)', url)
            post_id_val = post_id.group(1) if post_id else "0"
            
            # 카테고리 (게시판 이름) - 타이틀이나 네비게이션바에서 추출 시도
            title_node = soup.find(id="bo_v_title")
            if not title_node:
                title_node = soup.find(class_="bo_v_tit")
            title_text = title_node.get_text(strip=True) if title_node else ""

            # 보통 제목 위에 카테고리가 있거나, URL bo_table 파라미터 사용
            category_code = re.search(r'bo_table=([^&]+)', url)
            category = category_code.group(1) if category_code else "Unknown"

            # 본문 추출
            content_div = soup.find(id="bo_v_con") or soup.find(class_="view-content")
            if not content_div:
                print(f"⚠️ Error: ID {post_id_val} 본문 없음 - 건너뜀")
                return

            # HTML Cleaning
            clean_content = self.clean_text(content_div.get_text("\n", strip=True))
            
            # [Logic Update] Keyword Filtering
            if keyword:
                if (keyword not in title_text) and (keyword not in clean_content):
                    # 키워드가 제목이나 본문에 없으면 건너뜀
                    return
            
            # Smart Chunking
            chunks = self.smart_chunking(clean_content)
            tags = self.extract_tags(clean_content)
            date_str = datetime.now().strftime("%Y-%m-%d") # 실제 작성일을 파싱하려면 별도 로직 필요 (현재는 오늘 날짜)

            # 데이터 저장 구조 생성
            for idx, chunk in enumerate(chunks, 1):
                self.raw_data.append({
                    "ID": f"{post_id_val}_{idx}", # Unique ID for chunk
                    "Date": date_str,
                    "Category": category,
                    "Original_Text": chunk,
                    "Tags": tags,
                    "Target_Lang": "",     # 빈칸
                    "Translated_Text": ""  # 빈칸
                })
            
            print(f"✅ ID {post_id_val} 수집 완료 (청크: {len(chunks)}개)")

        except Exception as e:
            print(f"❌ Error: ID {url} 처리 중 오류 - {e}")

    def save_csv(self):
        """CSV 파일로 저장"""
        if not self.raw_data:
            print("⚠️ 저장할 데이터가 없습니다.")
            return

        df = pd.DataFrame(self.raw_data)
        file_name = "moim_raw_data.csv"
        
        # 기존 파일이 있다면 이어서 저장 (Append)
        if os.path.exists(file_name):
            df.to_csv(file_name, mode='a', header=False, index=False, encoding='utf-8-sig')
            print(f"💾 {len(df)}개 데이터를 기존 파일에 추가했습니다.")
        else:
            df.to_csv(file_name, index=False, encoding='utf-8-sig')
            print(f"💾 새로운 파일 {file_name}을 생성했습니다.")

if __name__ == "__main__":
    print("--- 🤖 Pure Community Data Collector ---")
    phpsessid_input = input("🔑 PHPSESSID 입력: ").strip()
    target_url = input("🔗 수집할 게시판 URL (예: ...bo_table=free): ").strip()
    pages_input = input("📄 수집할 페이지 수 (기본 1): ").strip()
    
    pages = int(pages_input) if pages_input.isdigit() else 1
    
    collector = PureCollector(phpsessid_input)
    
    print("\n🚀 수집을 시작합니다...")
    target_links = collector.get_board_links(target_url, pages)
    
    print(f"\n🔍 총 {len(target_links)}개의 게시글을 상세 수집합니다.")
    for link in target_links:
        collector.process_post(link)
        time.sleep(0.5)
        
    collector.save_csv()
    print("\n✨ 모든 작업이 완료되었습니다.")
