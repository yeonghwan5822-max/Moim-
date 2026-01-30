import sys
import os
import time
import random
import logging
import json
import socket
from urllib.parse import urlparse
from typing import List, Dict, Optional
from dotenv import load_dotenv

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrapy.selector import Selector

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from skills.crawler.driver import get_chrome_driver

# Load Environment Variables from backend/.env
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(env_path)

TARGET_BASE = os.getenv("TARGET_URL", "http://m.ebcblue.com")
LOGIN_URL = f"{TARGET_BASE}/bbs/login.php"
EBC_ID = os.getenv("EBC_ID")
EBC_PW = os.getenv("EBC_PW")

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class EbcCrawler:
    def __init__(self, headless: bool = False): # Default OFF for debugging
        self.driver = None
        self.headless = headless
        self.wait = None
        self.is_logged_in = False

    def _init_driver(self):
     import os
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager

        if not self.driver:
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")

            # 클라우드(리눅스) vs 로컬(맥북) 자동 감지
            if os.path.exists("/usr/bin/chromedriver"):
                service = Service("/usr/bin/chromedriver")
            else:
                service = Service(ChromeDriverManager().install())
                # 로컬에서는 헤드리스 끄기 (테스트용)
                if not self.headless:
                    options.arguments.remove("--headless")

            self.driver = webdriver.Chrome(service=service, options=options)
            
            options = Options()
            
            # --- 1. Define Options ---
            # Cloud Mandates (Applied if we detect Cloud, or if Headless requested)
            # We strictly apply these for Cloud stability.
            cloud_options = [
                "--headless", 
                "--no-sandbox", 
                "--disable-dev-shm-usage", 
                "--disable-gpu",
                "--disable-blink-features=AutomationControlled"
            ]
            
            # Check Environment: Streamlit Cloud usually has /usr/bin/chromedriver
            system_driver_path = "/usr/bin/chromedriver"
            is_cloud_env = os.path.exists(system_driver_path)
            
            if is_cloud_env:
                logging.info(f"☁️  Cloud Environment Detected. Using system driver: {system_driver_path}")
                service = Service(system_driver_path)
                # Apply Mandatory Cloud Options
                for opt in cloud_options:
                    options.add_argument(opt)
            else:
                logging.info("💻  Local Environment Detected. Using webdriver_manager.")
                service = Service(ChromeDriverManager().install())
                # Local Options
                options.add_argument("--disable-blink-features=AutomationControlled")
                options.add_argument("--window-size=1920,1080")
                if self.headless:
                    options.add_argument("--headless=new")
            
            try:
                self.driver = webdriver.Chrome(service=service, options=options)
                self.wait = WebDriverWait(self.driver, 10)
            except Exception as e:
                logging.error(f"❌ Driver Init Failed: {e}")
                raise e

    def check_domain_availability(self, url: str) -> bool:
        """
        DNS Lookup to check if domain exists before Selenium tries to access it.
        """
        try:
            domain = urlparse(url).netloc
            socket.gethostbyname(domain)
            logging.info(f"Domain '{domain}' resolved successfully.")
            return True
        except socket.error:
            logging.error(f"Domain resolution failed for '{url}'. The site might be down or invalid.")
            return False

    def handle_alert(self) -> Optional[str]:
        """
        Check for and dismiss unexpected alerts. Returns alert text if found, else None.
        """
        try:
            alert = self.wait.until(EC.alert_is_present())
            alert_text = alert.text
            logging.warning(f"Pop-up Alert detected: {alert_text}")
            alert.accept()
            time.sleep(random.uniform(0.8, 1.5))
            return alert_text
        except:
            return None

    def login(self):
        """
        Direct Login via login.php with Specific Selectors & Alert Handling.
        """
        self._init_driver()
        
        if self.is_logged_in:
            return

        if not EBC_ID or not EBC_PW:
            msg = "EBC_ID or EBC_PW missing in .env! Please set credentials."
            logging.error(msg)
            print(f"⚠️  {msg}")
            return

        # Direct Login URL Access
        logging.info(f"Navigating to Login Page: {LOGIN_URL}")
        try:
            self.driver.get(LOGIN_URL)
            self.handle_alert() 
            
            # 1. Specific Selectors (GnuBoard Standard)
            try:
                id_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='mb_id']")))
                pw_input = self.driver.find_element(By.CSS_SELECTOR, "input[name='mb_password']")
                
                # Debug Input
                logging.info(f"Inputting ID: {EBC_ID[:3]}***")
                id_input.clear()
                id_input.send_keys(EBC_ID)
                
                logging.info(f"Inputting PW: {'*' * len(EBC_PW)}")
                pw_input.clear()
                pw_input.send_keys(EBC_PW)
                
                # Verify Input (Optional Debug)
                if id_input.get_attribute('value') != EBC_ID:
                    logging.warning("⚠️ ID Input mismatch! Selenium might have failed to type correct ID.")
                
                # 2. Click Login Button
                try:
                    login_btn = self.driver.find_element(By.CSS_SELECTOR, "#login_fs input[type='image'], #login_fs button, .btn_login")
                    login_btn.click()
                except:
                    pw_input.submit() 
                    
                logging.info("Credentials submitted. Waiting for session verification...")
                
            except Exception as e:
                logging.error(f"Failed to find/input credentials: {e}")
                with open("login_fail.html", "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
                return

            time.sleep(random.uniform(2.0, 3.5)) # Wait for reload
            
            # Check Alert (e.g., Wrong Password)
            alert_txt = self.handle_alert()
            if alert_txt:
                logging.error(f"Login Failed due to Alert: {alert_txt}")
                # Analyze alert text?
                if "비밀번호" in alert_txt or "회원" in alert_txt:
                    return # Stop logic, failed.
            
            # 3. Strict Verification (Logout / MyPage / User Name)
            # User requirement: Wait until text appears
            try:
                # Wait for redirection to main or board
                success_element = self.wait.until(EC.presence_of_element_located(
                     (By.XPATH, "//a[contains(text(), '로그아웃')] | //a[contains(@href, 'logout')] | //a[contains(text(), '마이페이지')] | //span[contains(text(), '님')]")
                ))
                
                # Double check visible text if needed
                logging.info(f"✅ Login SUCCESS: Found session indicator '{success_element.text or 'icon'}'")
                self.is_logged_in = True
                
            except Exception as e:
                logging.error("❌ Login Verification Failed: Timeout waiting for 'Logout' or 'MyPage'.")
                self.is_logged_in = False
                # Optionally retry?

        except Exception as e:
            logging.error(f"Login process failed: {e}")
            self.handle_alert()

    def handle_alert(self):
        """
        Check for and dismiss unexpected alerts (e.g., 'Search term required').
        """
        try:
            alert = self.wait.until(EC.alert_is_present())
            alert_text = alert.text
            logging.warning(f"Dismissing Alert: {alert_text}")
            alert.accept()
            time.sleep(1)
            return True
        except:
            return False

    def get_categorized_links(self, board_url: str, keyword: str, max_pages: int = 1) -> Dict:
        """
        Classifies links based on keyword matching.
        Returns: {'category': keyword, 'found_links': [...]}
        """
        self.login()
        base_url = board_url if board_url.startswith("http") else f"{TARGET_BASE}{board_url}"
        
        all_found = []
        # Reuse get_post_links but maybe we need to fetch ALL first then filter? 
        # Actually efficiently, we can just use get_post_links with the keyword, 
        # but the user asked to "Collect title/url first, then filter".
        # To be safe and efficient, we can reuse get_post_links logic but strictly structure the output.
        
        # Let's delegate to get_post_links which already handles pagination/parsing
        raw_links = self.get_post_links(board_url, keyword=keyword, max_pages=max_pages)
        
        return {
            "category": keyword,
            "found_count": len(raw_links),
            "found_links": raw_links
        }

    def classify_topic(self, text: str) -> str:
        """
        Simple Keyword-based Topic Classifier
        """
        keywords = {
            "실습": ["실습", "작업", "봉사", "현장"],
            "전도": ["전도", "복음", "영접"],
            "수양회": ["수양회", "수련회", "캠프", "리트릿"],
            "모임": ["모임", "교제", "순모임", "지체"]
        }
        
        for topic, keys in keywords.items():
            if any(k in text for k in keys):
                return topic
        return "기타"

    def get_post_links(self, board_url: str, keyword: str = None, max_pages: int = 1) -> List[Dict]:
        """
        Robust Auto-Discovery using BeautifulSoup and Alert Handling.
        """
        from bs4 import BeautifulSoup
        
        # Ensure Login
        self.login()
        collected_links = []
        seen_urls = set()
        
        base_url = board_url if board_url.startswith("http") else f"{TARGET_BASE}{board_url}"
        
        if not self.check_domain_availability(base_url):
            return []

        for page in range(1, max_pages + 1):
            if "?" in base_url:
                current_url = f"{base_url}&page={page}"
            else:
                current_url = f"{base_url}?page={page}"
            
            logging.info(f"Scanning Page {page}: {current_url}")
            try:
                self.driver.get(current_url)
                
                # Check for Alert immediately after navigation
                self.handle_alert()
                
                # Wait for Body
                self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            except Exception as e:
                # If alert failed to be caught above, catching execution error
                if "unexpected alert open" in str(e):
                    logging.warning(f"Alert interrupted page load. Retrying after dismissal.")
                    self.handle_alert()
                else:
                    logging.warning(f"Page {page} navigation error: {e}")
                    continue
            
            # Use BeautifulSoup for flexible parsing
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            all_links = soup.find_all('a', href=True)
            
            page_count = 0
            for link in all_links:
                try:
                    href = link['href']
                    text = link.get_text(strip=True)
                    title_attr = link.get('title', '').strip()
                    
                    # Skip empty links
                    if not href or (len(href) < 2 and not text): continue
                    
                    # 1. Keyword Check
                    is_match = False
                    if keyword:
                        if (keyword in text) or (keyword in title_attr):
                            is_match = True
                        else:
                            # Fuzzy Context Search: Check parent text?
                            parent_text = link.parent.get_text(strip=True)
                            if keyword in parent_text:
                                is_match = True
                    else:
                        is_match = True # No keyword = collect all
                    
                    if not is_match: continue
                    
                    # 2. Filter Junk
                    if any(x in href for x in ['javascript:', '#', 'logout', 'login', 'write']):
                        continue
                        
                    # 3. Absolute URL
                    if not href.startswith("http"):
                        if href.startswith("/"):
                            full_url = f"{TARGET_BASE}{href}"
                        else:
                            # Relative to board/
                            if 'bbs' in base_url and 'bbs' not in href:
                                full_url = f"{TARGET_BASE}/bbs/{href}"
                            else:
                                full_url = f"{TARGET_BASE}/{href}"
                    else:
                        full_url = href
                        
                    # Dedupe
                    if full_url in seen_urls: continue
                    seen_urls.add(full_url)
                    
                    collected_links.append({"title": text, "url": full_url})
                    page_count += 1
                    
                except Exception as e:
                    continue
            
            logging.info(f"Page {page}: Found {page_count} items matching '{keyword}'.")
            time.sleep(random.uniform(0.5, 1.5))

        return collected_links

    def crawl_detail(self, url: str, title: str) -> Dict:
        """
        Crawls detail page with robust strategies:
        1. Multi-Selectors
        2. IFRAME Traversal
        3. Text Density Fallback (Heuristic)
        """
        # Ensure Login
        self.login()
        logging.info(f"Crawling Detail: {url}")
        
        if not self.check_domain_availability(url):
            return {"status": "error", "reason": "DNS Resolution Failed (Invalid Domain)"}

        try:
            self.driver.get(url)
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # Check for Alerts (Login required, etc.)
            alert_txt = self.handle_alert()
            if alert_txt:
                logging.warning(f"Detail Page Alert: {alert_txt}")
                # Re-login Loop Logic
                if "권한" in alert_txt or "회원" in alert_txt or "로그인" in alert_txt:
                    logging.info("🔄 Session lost or insufficient level. Attempting Re-login...")
                    self.is_logged_in = False # Force reset
                    self.login()
                    
                    if self.is_logged_in:
                         logging.info("Re-login successful. Retrying page access...")
                         self.driver.get(url)
                         if self.handle_alert(): # Check if blocked again
                             return {"status": "error", "reason": "Access Denied even after Re-login (Level insufficient?)"}
                    else:
                        return {"status": "error", "reason": "Re-login Failed"}
                else:
                    return {"status": "error", "reason": f"Page blocked by Alert: {alert_txt}"}

            # Strategy 1: Explicit Selectors
            # Mobile & Desktop variants
            selectors = [
                 "#bo_v_atc", "#bo_v_con", ".view_content", ".board_view_content", 
                 ".post_text", ".article_body", "#article_body", "div[itemprop='articleBody']",
                 ".content", "article", "#vContent"
            ]
            
            from bs4 import BeautifulSoup
            
            def get_cleaned_soup(driver_source):
                soup = BeautifulSoup(driver_source, 'html.parser')
                
                # 1. Global Noise Removal (Decompose)
                # Remove Script/Style
                for tag in soup(["script", "style", "noscript", "iframe", "svg"]):
                    tag.extract()

                # Remove Layout/Ad Noise (Classes & IDs)
                noise_selectors = [
                    # GnuBoard/Common Noise
                    "#bo_v_sns", "#bo_v_file", ".bo_v_file", "#bo_v_link", ".bo_v_link",
                    "#bo_v_top", ".bo_v_com", "#bo_vc", "section#bo_vc", # Comments
                    ".bo_v_nb", ".bo_v_ad", "#bo_v_ad", 
                    # Generic Noise
                    "header", "footer", "nav", ".nav", ".menu", ".sidebar", 
                    ".ads", ".advertisement", ".banner", ".popup",
                    ".btn", ".button", "button", 
                    ".reply", ".comment", "#comment", ".comments",
                    ".copyright", ".footer"
                ]
                
                for selector in noise_selectors:
                    for tag in soup.select(selector):
                        tag.decompose()
                        
                return soup

            def extract_by_selector(soup_obj):
                for sel in selectors:
                    element = soup_obj.select_one(sel)
                    if element:
                        txt = element.get_text(separator="\n", strip=True)
                        if len(txt) > 20: # Minimal meaningful length
                            logging.info(f"Found content via selector: {sel}")
                            return txt
                return None
            
            def extract_by_density(soup_obj):
                # Fallback: Find div with max text length
                max_len = 0
                best_text = None
                
                # Check divs, articles, sections
                for tag in soup_obj.find_all(['div', 'article', 'section', 'td']):
                    # Skip common junk classes
                    cls = " ".join(tag.get('class', []))
                    if any(x in cls for x in ['menu', 'nav', 'foot', 'banner', 'login']):
                        continue
                        
                    txt = tag.get_text(separator="\n", strip=True)
                    if len(txt) > max_len:
                        max_len = len(txt)
                        best_text = txt
                
                if best_text and max_len > 50: # Threshold
                    logging.info(f"Found content via Text Density (Len: {max_len})")
                    return best_text
                return None

            # Attempt 1: Main Frame
            soup = get_cleaned_soup(self.driver.page_source)
            content_text = extract_by_selector(soup)
            
            if not content_text:
                content_text = extract_by_density(soup) # Fallback 1

            # Attempt 2: Iframes (Recursive-ish)
            if not content_text:
                iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
                if iframes:
                    logging.info(f"Checking {len(iframes)} iframes for content...")
                    for i, frame in enumerate(iframes):
                        try:
                            self.driver.switch_to.frame(frame)
                            iframe_soup = get_cleaned_soup(self.driver.page_source)
                            
                            # Try Selectors in Iframe
                            content_text = extract_by_selector(iframe_soup)
                            if not content_text:
                                content_text = extract_by_density(iframe_soup)
                            
                            self.driver.switch_to.default_content() # Reset
                            
                            if content_text:
                                logging.info(f"Found content in iframe #{i}")
                                break
                        except:
                            self.driver.switch_to.default_content()

            if not content_text:
                 # Last resort Dump
                 with open("content_fail_dump.html", "w", encoding="utf-8") as f:
                     f.write(self.driver.page_source)
                 return {"status": "error", "reason": "Content not found (Selectors & Density failed). Dump saved."}

            return {
                "status": "success",
                "title": title,
                "url": url,
                "content": content_text,
                "timestamp": time.time()
            }
            
        except Exception as e:
            logging.error(f"Failed detail crawl: {e}")
            return {"status": "error", "reason": f"Runtime Exception: {str(e)}"}

    def close(self):
        if self.driver:
            self.driver.quit()

def main_mock_test():
    """
    Simulation / Mock Test Mode
    """
    print("Running Mock Test...")
    # Mock behavior simulating what the crawler WOULD return
    data = [
        {"title": "[Mock] 이번주 실습 안내", "url": "http://mock/1", "content": "mock content 1"},
        {"title": "[Mock] 교제 모임 후기", "url": "http://mock/2", "content": "mock content 2"}
    ]
    print(f"Collected {len(data)} mock items.")
    return data

if __name__ == "__main__":
    # Simple CLI Test switch
    # If args provided, try real crawl, else mock?
    # Let's just try real crawl with safety
    crawler = EbcCrawler(headless=False)
    try:
        crawler.login()
        res = crawler.get_post_links("/bbs/board.php?bo_table=practice", keyword="실습")
        print(f"Links: {len(res)}")
    finally:
        crawler.close()
