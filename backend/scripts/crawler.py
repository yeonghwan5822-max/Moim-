import sys
import os
import shutil
import time
from typing import List

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

# 로컬 테스트용 (없어도 됨)
try:
    from webdriver_manager.chrome import ChromeDriverManager
except ImportError:
    ChromeDriverManager = None

class EbcCrawler:
    def __init__(self, headless: bool = False):
        self.driver = None
        self.headless = headless
        self._init_driver()

    def _init_driver(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        
        # 1. 시스템에 있는 크롬 자동 추적 (가장 중요!)
        # 이름이 chromium이든 chromium-browser든 다 찾아봄
        bin_path = shutil.which("chromium") or shutil.which("chromium-browser") or "/usr/bin/chromium"
        driver_path = shutil.which("chromedriver") or "/usr/bin/chromedriver"
        
        # 2. 클라우드 환경 감지
        if bin_path and os.path.exists(bin_path) and os.path.exists(driver_path):
            print(f"🚀 Cloud Environment: Found {bin_path}")
            options.binary_location = bin_path
            service = Service(driver_path)
        
        # 3. 로컬(맥북) 환경 감지
        else:
            print("💻 Local Environment: Using Webdriver Manager")
            if ChromeDriverManager:
                service = Service(ChromeDriverManager().install())
                if not self.headless:
                    options.arguments.remove("--headless")
            else:
                raise ImportError("Local testing requires webdriver_manager")

        self.driver = webdriver.Chrome(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 10)

    def close(self):
        if self.driver:
            self.driver.quit()

    def login(self):
        pass

    def get_post_links(self, board_url: str, keyword: str = None) -> List[str]:
        # 테스트: 드라이버가 켜지면 성공
        self.driver.get(board_url)
        return []
