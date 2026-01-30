from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
import os
import json
from skills.analyzer.model import OOVAnalyzer
# from skills.crawler.driver import get_chrome_driver # Defer import to avoid immediate browser launch

app = FastAPI(title="Moim Translator API", version="0.1.0")

# In-memory storage for PoC
oov_results = []

class CrawlRequest(BaseModel):
    url: str
    deep_scan: bool = False

@app.get("/")
def read_root():
    return {"status": "ok", "service": "Moim Translator Backend"}

@app.post("/crawl")
def start_crawl(req: CrawlRequest, background_tasks: BackgroundTasks):
    """
    Trigger a crawl task (Mocked for PoC integration step).
    Real implementation would invoke Scrapy/Selenium here.
    """
    background_tasks.add_task(mock_crawl_task, req.url)
    return {"message": "Crawl started", "target": req.url}

@app.get("/oov")
def get_oov_candidates():
    """
    Return the latest OOV words extracted.
    """
    if not oov_results:
        # Return dummy data if empty so frontend dev can proceed
        return [
            {"word": "작업지원", "score": 0.95, "tag": "Practical"},
            {"word": "교제", "score": 0.88, "tag": "University"},
            {"word": "지체", "score": 0.82, "tag": "Biblical"},
        ]
    return oov_results

def mock_crawl_task(url: str):
    # Simulate processing time
    import time
    time.sleep(2)
    print(f"Finished crawling {url}")
