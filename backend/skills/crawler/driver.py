import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def get_chrome_driver(headless=True):
    """
    Returns a configured Chrome WebDriver instance.
    Includes anti-detection measures and headless mode options.
    """
    chrome_options = Options()
    
    if headless:
        chrome_options.add_argument("--headless=new")  # Modern headless mode
    
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Anti-detection: Disable 'navigator.webdriver' flag
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    
    # User Agent to look like a regular browser
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Execute CDP command to modify navigator.webdriver flag
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        """
    })
    
    logging.info("Chrome Driver initialized successfully.")
    return driver

if __name__ == "__main__":
    # Test driver
    driver = get_chrome_driver(headless=True)
    driver.get("https://www.google.com")
    print(f"Driver Test: {driver.title}")
    driver.quit()
