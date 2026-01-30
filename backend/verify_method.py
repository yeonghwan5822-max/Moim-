import sys
import os
import logging

# Ensure project root is in path
sys.path.append(os.path.abspath("."))

try:
    from scripts.crawler import EbcCrawler
    logging.basicConfig(level=logging.INFO)

    print("--- Verification Start ---")
    crawler = EbcCrawler(headless=True)
    
    if hasattr(crawler, 'get_post_links'):
        print("✅ SUCCESS: Method 'get_post_links' exists.")
        
        # Dry run call
        print("Testing method call...")
        try:
            # Use simulation/mock URL or real one, but just check if it runs without Attribute Error
            # We assume it might fail networking if site is down, but method error is what we check.
            links = crawler.get_post_links("/bbs/mock_test", keyword="test", max_pages=1)
            print(f"Method called successfully. Result type: {type(links)}")
        except Exception as e:
            print(f"Method call error (runtime): {e}")
    else:
        print("❌ FAILURE: Method 'get_post_links' NOT found.")

    crawler.close()
    print("--- Verification End ---")

except Exception as e:
    print(f"Import/Setup Error: {e}")
