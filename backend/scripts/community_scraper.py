
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import re
from datetime import datetime
import urllib3
from urllib.parse import urljoin

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class CommunityScraper:
    def __init__(self, base_url, phpsessid):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.cookies.set('PHPSESSID', phpsessid)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': base_url,
        }
        self.keywords = ['중도', '학식', '과잠', '팀플']
        self.data_store = []

    def fetch_page(self, url):
        """Fetches a page with error handling."""
        try:
            response = self.session.get(url, headers=self.headers, verify=False, timeout=10)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            return response.text
        except Exception as e:
            print(f"❌ Error fetching {url}: {e}")
            return None

    def parse_list_page(self, list_url):
        """Parses the list page to find post links."""
        html = self.fetch_page(list_url)
        if not html:
            return []

        soup = BeautifulSoup(html, 'html.parser')
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            # Improved filtering based on victory.py observations
            if 'wr_id=' in href and 'bo_table=' in href:
                if any(x in href for x in ['write', 'update', 'delete', 'search']):
                    continue
                full_link = urljoin(self.base_url, href)
                links.append(full_link)
        
        # Deduplicate links
        return list(set(links))

    def smart_chunking(self, text, max_length=1000):
        """Splits text into chunks if it exceeds max_length, based on sentence delimiters."""
        if len(text) <= max_length:
            return [text]

        chunks = []
        current_chunk = ""
        
        # Split by sentence endings (. ? \n) but keep the delimiter
        # Regex explanation: (?<=[.?\n]) looks behind for delimiters to split after them
        sentences = re.split(r'(?<=[.?\n])', text)
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) > max_length:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence
            else:
                current_chunk += sentence
        
        if current_chunk:
            chunks.append(current_chunk)
            
        return chunks

    def extract_tags(self, text):
        """Extracts keywords from text."""
        found_tags = [kw for kw in self.keywords if kw in text]
        return ",".join(found_tags) if found_tags else ""

    def process_post(self, url):
        """Extracts content from a post page and processes it."""
        print(f"Processing: {url}")
        html = self.fetch_page(url)
        if not html:
            return

        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract metadata
        try:
            title = soup.find('h1', id='bo_v_title')
            if not title: # Fallback
                title = soup.find(['h1', 'h2', 'title'])
            title_text = title.get_text(strip=True) if title else "No Title"

            # Assuming dates look like 2024-XX-XX or similar, often found in meta or specific span
            # Using a generic finder for now as structure varies; user prompt implies it exists
            date_element = soup.find(text=re.compile(r'\d{4}-\d{2}-\d{2}')) 
            date_text = date_element.strip() if date_element else datetime.now().strftime("%Y-%m-%d")

            # Category/Board Name - often in title or breadcrumb
            category = "Unknown" 
            # Parse 'bo_table' from URL for a rough category if not found
            if 'bo_table=' in url:
                category = url.split('bo_table=')[1].split('&')[0]

            # Content Extraction
            content_div = soup.find(id="bo_v_con") or soup.find(class_="view-content")
            if not content_div:
                print(f"⚠️ No content found for {url}")
                return

            # Clean Content (remove scripts, styles)
            for script in content_div(["script", "style"]):
                script.decompose()
            
            original_text = content_div.get_text("\n", strip=True)
            
            # Smart Pre-processing
            chunks = self.smart_chunking(original_text)
            tags = self.extract_tags(original_text)
            
            # Add to Data Store
            group_id = url.split('wr_id=')[1].split('&')[0] # Use post ID as Group ID
            
            for idx, chunk in enumerate(chunks, 1):
                entry = {
                    'ID': f"{group_id}_{idx}",
                    'Group_ID': group_id,
                    'Seq': idx,
                    'Date': date_text,
                    'Category': category,
                    'Tags': tags,
                    'Original_Text': chunk,
                    'English_Text': "",
                    'Cultural_Note': "",
                    'Glossary_Used': ""
                }
                self.data_store.append(entry)

        except Exception as e:
            print(f"⚠️ Error parsing {url}: {e}")

    def run(self, start_url, max_pages=1):
        """Main execution flow."""
        print("🚀 Starting Scraper...")
        
        all_links = []
        # Support pagination if needed, for now just scraping the start_url list
        # If headers/params needed for paging, can be added
        
        print(f"Scanning list page: {start_url}")
        links = self.parse_list_page(start_url)
        print(f"Found {len(links)} posts.")
        all_links.extend(links)
            
        for link in all_links:
            self.process_post(link)
            time.sleep(1) # Polite delay
        
        self.save_data()
        print("✅ Scraping Completed.")

    def save_data(self):
        """Saves data to CSV/Excel."""
        if not self.data_store:
            print("⚠️ No data to save.")
            return

        df = pd.DataFrame(self.data_store)
        
        # Ensure column order
        cols = ['ID', 'Group_ID', 'Seq', 'Date', 'Category', 'Tags', 'Original_Text', 
                'English_Text', 'Cultural_Note', 'Glossary_Used']
        
        # Add missing columns if any
        for col in cols:
            if col not in df.columns:
                df[col] = ""
                
        df = df[cols]
        
        output_file = "community_data.csv"
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"💾 Data saved to {os.path.abspath(output_file)}")

if __name__ == "__main__":
    # Example Usage - Replace with real PHPSESSID and URL
    # Can be run via command line or modified here
    TARGET_URL = "https://m.ebcblue.com/bbs/board.php?bo_table=free" # Example
    PHPSESSID = "YOUR_PHPSESSID_HERE" 
    
    # Prompt for input if running interactively
    print("--- Community Data Scraper ---")
    if PHPSESSID == "YOUR_PHPSESSID_HERE":
        PHPSESSID = input("Enter PHPSESSID: ").strip()
    
    scraper = CommunityScraper(TARGET_URL.split('?')[0], PHPSESSID) # Pass base URL
    scraper.run(TARGET_URL)
