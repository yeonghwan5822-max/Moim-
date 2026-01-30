import requests
from bs4 import BeautifulSoup
import streamlit as st
from urllib.parse import urljoin, quote
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class EbcCrawler:
    def __init__(self, **kwargs):
        self.session = requests.Session()
        # [핵심] 봇 차단 회피용 헤더
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://m.ebcblue.com/',
            'Accept-Language': 'ko-KR,ko;q=0.9'
        }

    def _init_driver(self): pass
    def close(self): pass

    def get_categorized_links(self, url, keyword=None, *args, **kwargs):
        # 검색어 유무에 따른 분기 처리
        if keyword:
            st.info(f"🚀 [검색 모드] 키워드 '{keyword}'로 직접 접근합니다.")
            encoded_kw = quote(keyword.encode('utf-8'))
            sep = "&" if "?" in url else "?"
            # 검색 쿼리 직접 주입
            target_url = f"{url}{sep}sfl=wr_subject||wr_content&stx={encoded_kw}"
        else:
            st.info(f"📡 [목록 모드] 전체 목록을 스캔합니다.")
            target_url = url

        links = self.get_post_links(target_url, keyword)
        return {'notice': [], 'normal': links}

    def get_post_links(self, url, keyword=None):
        links = []
        try:
            # 1. 메인 페이지 방문 (쿠키 획득)
            self.session.get("https://m.ebcblue.com/", headers=self.headers, verify=False, timeout=5)
            
            # 2. 실제 타겟 페이지 접속
            res = self.session.get(url, headers=self.headers, verify=False, timeout=15)
            res.encoding = res.apparent_encoding
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # [진단] 현재 페이지 상황 출력
            all_a = soup.find_all('a', href=True)
            with st.expander(f"🕵️‍♂️ 페이지 진단 (링크 {len(all_a)}개 발견)", expanded=True):
                if not all_a:
                    st.warning("링크가 0개입니다. 봇 차단되었거나 로그인이 필요할 수 있습니다.")
                for a in all_a[:3]:
                    st.text(f"샘플: [{a.get_text(strip=True)}] -> {a['href']}")

            # 3. 링크 수집
            for a in all_a:
                href = a['href']
                # wr_id 패턴 확인
                if 'wr_id=' in href:
                    if any(bad in href for bad in ['write', 'update', 'delete', 'search', 'login']): continue
                    
                    full_link = urljoin(url, href)
                    
                    # 이미 검색된 페이지라면(stx 포함) 키워드 검사 불필요
                    if "stx=" in url:
                        if full_link not in links: links.append(full_link)
                    # 일반 목록이라면 텍스트 검사
                    elif not keyword or (keyword in a.get_text() or keyword in full_link):
                        if full_link not in links: links.append(full_link)
            
            if links:
                st.success(f"🎯 {len(links)}개의 게시글을 확보했습니다!")
            return links

        except Exception as e:
            st.error(f"❌ 접속 오류: {e}")
            return []

    def get_post_content(self, url):
        try:
            res = self.session.get(url, headers=self.headers, verify=False, timeout=10)
            res.encoding = res.apparent_encoding
            soup = BeautifulSoup(res.text, 'html.parser')
            title = soup.find(['h1', 'h2', 'title'])
            content = soup.find(id="bo_v_con") or soup.find(class_="view-content") or soup.body
            return {
                'title': title.get_text(strip=True) if title else "제목 없음",
                'content': content.get_text(strip=True) if content else "본문 없음",
                'date': '2026-01-31'
            }
        except: return {'title': 'Error', 'content': '', 'date': ''}
