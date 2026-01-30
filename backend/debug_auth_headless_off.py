import sys
import os
import logging

# Add project root
sys.path.append(os.path.abspath("."))
from scripts.crawler import EbcCrawler

# Logging
logging.basicConfig(level=logging.INFO)

print("--- Debugging Login (Headless OFF) ---")
# Force Headless False as requested
crawler = EbcCrawler(headless=False)
try:
    crawler.login()
    
    if crawler.is_logged_in:
        print("\n✅ LOGIN SUCCESS!")
    else:
        print("\n❌ LOGIN FAILED (Check browser window for details)")
        
    input("Press Enter to close browser...") # Keep browser open to see result
except Exception as e:
    print(f"Error: {e}")
finally:
    crawler.close()
