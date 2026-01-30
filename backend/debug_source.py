import sys
import os
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Add project root to path
sys.path.append(os.path.abspath("."))
from scripts.crawler import EbcCrawler

# Setup Logging
logging.basicConfig(level=logging.INFO)

def debug_run():
    crawler = EbcCrawler(headless=True)
    target = "http://m.ebcblue.com/bbs/board.php?bo_table=practice"
    
    print(f"--- Debugging: {target} ---")
    try:
        # 1. Login
        crawler.login()
        
        # 2. Go to Board
        print(f"Navigating to board: {target}")
        crawler.driver.get(target)
        
        # 3. Dump Source
        source = crawler.driver.page_source
        print(f"\n[Page Source Dump (First 2000 chars)]:\nStart----------------\n{source[:2000]}\n----------------End")
        
        # 4. Check Title/Structure
        if "login" in crawler.driver.current_url:
            print("\n[Diagnosis]: Redirected to Login Page (Login Failed or Session Lost).")
        elif "list_board" in source or "li" in source:
             print("\n[Diagnosis]: List seems present (found 'li' or 'list_board').")
        else:
             print("\n[Diagnosis]: Structure Unclear.")
             
    except Exception as e:
        print(f"Error: {e}")
    finally:
        crawler.close()

if __name__ == "__main__":
    debug_run()
