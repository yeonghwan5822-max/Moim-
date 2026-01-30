import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class EbcCrawler:
    def __init__(self, headless=True):
        self.driver = None
        self.headless = headless
        self._init_driver()

    def _init_driver(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        
        # 1. 클라우드 환경 (시스템 경로 강제)
        if os.path.exists("/usr/bin/chromium") and os.path.exists("/usr/bin/chromedriver"):
            print("🚀 Cloud Environment Detected: Using System Binaries")
            options.binary_location = "/usr/bin/chromium"
            service = Service("/usr/bin/chromedriver")
        
        # 2. 로컬 환경 (자동 다운로드)
        else:
            print("💻 Local Environment Detected: Using Webdriver Manager")
            service = Service(ChromeDriverManager().install())
            if not self.headless:
                options.arguments.remove("--headless")

        self.driver = webdriver.Chrome(service=service, options=options)

    def get_post_links(self, url, keyword=None):
        # 테스트: 페이지 접속 후 제목 출력
        print(f"Testing URL: {url}")
        self.driver.get(url)
        time.sleep(2)
        print(f"Page Title: {self.driver.title}")
        return []

    def close(self):
        if self.driver:
            self.driver.quit()
