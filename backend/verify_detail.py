import sys
import os
import logging
import time

# Ensure project root is in path
sys.path.append(os.path.abspath("."))

try:
    from scripts.crawler import EbcCrawler
    logging.basicConfig(level=logging.INFO)

    print("--- Verification Start: Single Page Crawl ---")
    crawler = EbcCrawler(headless=True)
    
    # Test 1: Invalid URL (Should report DNS error)
    print("\n[Test 1] Invalid URL...")
    res = crawler.crawl_detail("http://invalid-url-test-123.com", "Invalid Test")
    print(f"Result: {res}")
    
    if res.get("status") == "error":
        print("✅ Correctly identified error.")
    else:
        print("❌ Failed to report error.")

    # Test 2: Valid Domain but Mock Path (Should connect but fail content extraction if no selectors match)
    # Using a known safe domain that resolves but won't match our specific selectors usually
    print("\n[Test 2] Valid Domain / No Content...")
    # Using example.com or similar if we wanted, but let's use the target base to be safe on DNS check
    target = "http://m.ebcblue.com/" 
    res = crawler.crawl_detail(target, "Home Test")
    print(f"Result: {res}")
    
    # We expect either success (if it matches generic selectors) or error (content not found)
    # Key is it returns a Dict, not None/Crash.
    if isinstance(res, dict):
         print("✅ Returned Dict as expected.")
    else:
         print("❌ Returned non-dict.")

    crawler.close()
    print("--- Verification End ---")

except Exception as e:
    print(f"Runtime Error: {e}")
