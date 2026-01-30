import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

class EbcCrawler:
    def __init__(self, headless=True):
        self.driver = None
        # 클라우드에서는 무조건 headless 모드여야 함
        self.headless = True 
        self._init_driver()

    def _init_driver(self):
        options = Options()
        
        # [핵심] 127 에러 및 충돌 방지 5대장 옵션
        options.add_argument("--headless=new") # 구버전 headless보다 훨씬 안정적
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage") # 메모리 공유 에러 방지
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080") # 화면 크기 0으로 인한 에러 방지
        
        # 1. Streamlit Cloud 환경 (시스템 경로 강제)
        if os.path.exists("/usr/bin/chromium") and os.path.exists("/usr/bin/chromedriver"):
            print("🚀 Cloud Environment: Using System Binaries")
            options.binary_location = "/usr/bin/chromium"
            service = Service("/usr/bin/chromedriver")
        
        # 2. 로컬 환경 (Fallback)
        else:
            print("💻 Local Environment: Using Webdriver Manager")
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())

        try:
            self.driver = webdriver.Chrome(service=service, options=options)
            print("✅ 크롬 드라이버 시동 성공!")
        except Exception as e:
            print(f"❌ 크롬 시동 실패: {e}")
            raise e

    def get_post_links(self, url, keyword=None):
        print(f"Testing connection to: {url}")
        if self.driver:
            self.driver.get(url)
            time.sleep(1)
            print(f"Page Title: {self.driver.title}")
            return []
        return []

    def close(self):
        if self.driver:
            self.driver.quit()
