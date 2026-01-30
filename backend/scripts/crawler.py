import os
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By

class EbcCrawler:
    def __init__(self, headless=True):
        self.driver = None
        self.headless = headless
        self._init_driver()

    def _init_driver(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--window-size=1920,1080")
        
        # Streamlit Cloud 전용 설정 (파이어폭스)
        # 1. 시스템에 설치된 파이어폭스 드라이버(geckodriver) 위치
        service_path = "/usr/bin/geckodriver"
        binary_path = "/usr/bin/firefox"

        if os.path.exists(service_path) and os.path.exists(binary_path):
            print("🦊 Cloud Environment: Using Firefox & GeckoDriver")
            options.binary_location = binary_path
            service = Service(service_path)
        else:
            # 로컬(맥북) 테스트용 fallback
            print("💻 Local Environment: Using Webdriver Manager (Firefox)")
            from webdriver_manager.firefox import GeckoDriverManager
            service = Service(GeckoDriverManager().install())

        try:
            self.driver = webdriver.Firefox(service=service, options=options)
            print("✅ 파이어폭스 시동 성공!")
        except Exception as e:
            print(f"❌ 파이어폭스 시동 실패: {e}")
            raise e

    def get_post_links(self, url, keyword=None):
        print(f"Testing connection to: {url}")
        if self.driver:
            self.driver.get(url)
            time.sleep(2)
            print(f"Page Title: {self.driver.title}")
            return []
        return []

    def close(self):
        if self.driver:
            self.driver.quit()
