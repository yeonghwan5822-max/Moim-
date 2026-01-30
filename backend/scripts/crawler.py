import sys
import os
import time
import random
import logging
from urllib.parse import urlparse
from typing import List, Dict, Optional
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrapy.selector import Selector

# 로컬(맥북)에서만 필요한 라이브러리 (클라우드 에러 방지용 try-except)
try:
    from webdriver_manager.chrome import ChromeDriverManager
except ImportError:
    ChromeDriverManager = None

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class EbcCrawler:
    def __init__(self, headless: bool = False):
        self.driver = None
        self.headless = headless
        self.wait = None
        self.is_logged_in = False
        self._init_driver()

    def _init_driver(self):
        options = Options()
        # 기본 옵션 (클라우드 필수)
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        
        # 1. Streamlit Cloud 환경 (시스템 크롬 강제 사용)
        if os.path.exists("/usr/bin/chromium") and os.path.exists("/usr/bin/chromedriver"):
            print("🚀 Cloud Environment Detected: Using System Chromium")
            options.binary_location = "/usr/bin/chromium"  # 브라우저 위치 고정
            service = Service("/usr/bin/chromedriver")     # 드라이버 위치 고정
        
        # 2. 로컬 Mac 환경 (자동 다운로드)
        else:
            print("💻 Local Environment Detected: Using Webdriver Manager")
            if ChromeDriverManager:
                service = Service(ChromeDriverManager().install())
                # 로컬에서 시뮬레이션 모드가 아닐 때만 헤드리스 끄기
                if not self.headless:
                    options.arguments.remove("--headless")
            else:
                raise ImportError("webdriver_manager is required for local testing.")

        self.driver = webdriver.Chrome(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 10)

    def close(self):
        if self.driver:
            self.driver.quit()
            self.driver = None

    # --- (아래는 기능 함수들) ---
    def login(self):
        # 로그인 로직 (필요시 구현)
        pass

    def get_post_links(self, board_url: str, keyword: str = None) -> List[str]:
        # 테스트용 더미 데이터 반환 (실제 크롤링 로직은 여기에 구현)
        # 127 에러 해결 확인을 위해 드라이버가 켜지는지만 확인
        self.driver.get(board_url)
        time.sleep(2)
        page_source = self.driver.page_source
        print(f"Page Title: {self.driver.title}")
        return [] 
