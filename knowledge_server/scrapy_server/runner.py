"""
Scrapy runner for managing crawl jobs.
"""

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from scrapy import signals
from scrapy.crawler import CrawlerProcess
from scrapy.signalmanager import dispatcher

from knowledge_server.scrapy_server.spider import ContentSpider, SimpleSpider


class ScrapyRunner:
    """Runner for managing Scrapy crawl jobs."""
    
    def __init__(
        self,
        output_dir: Optional[str] = None,
        settings: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the Scrapy runner.
        
        Args:
            output_dir: Directory to store scraped data.
            settings: Optional Scrapy settings override.
        """
        self.output_dir = output_dir or tempfile.mkdtemp()
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        
        self.default_settings = {
            "LOG_LEVEL": "WARNING",
            "ROBOTSTXT_OBEY": True,
            "DOWNLOAD_DELAY": 1,
            "CONCURRENT_REQUESTS": 4,
            "DEPTH_LIMIT": 2,
            "FEEDS": {},
        }
        
        if settings:
            self.default_settings.update(settings)
        
        self.results: List[Dict[str, Any]] = []
    
    def _collect_items(self, item: Dict[str, Any]) -> None:
        """Callback to collect scraped items."""
        self.results.append(dict(item))
    
    def scrape_urls(
        self,
        urls: List[str],
        allowed_domains: Optional[List[str]] = None,
        follow_links: bool = False,
        max_depth: int = 2,
    ) -> List[Dict[str, Any]]:
        """
        Scrape content from URLs.
        
        Args:
            urls: List of URLs to scrape.
            allowed_domains: Optional list of allowed domains.
            follow_links: Whether to follow links on pages.
            max_depth: Maximum crawl depth if following links.
            
        Returns:
            List of scraped content dictionaries.
        """
        self.results = []
        
        settings = self.default_settings.copy()
        settings["DEPTH_LIMIT"] = max_depth
        
        process = CrawlerProcess(settings)
        
        # Connect signal to collect items
        dispatcher.connect(self._collect_items, signal=signals.item_scraped)
        
        if follow_links:
            process.crawl(
                ContentSpider,
                start_urls=urls,
                allowed_domains=allowed_domains,
                max_depth=max_depth,
            )
        else:
            process.crawl(SimpleSpider, start_urls=urls)
        
        process.start()
        
        return self.results
    
    def scrape_to_file(
        self,
        urls: List[str],
        output_file: str,
        allowed_domains: Optional[List[str]] = None,
        follow_links: bool = False,
    ) -> str:
        """
        Scrape content and save to file.
        
        Args:
            urls: List of URLs to scrape.
            output_file: Output file name.
            allowed_domains: Optional list of allowed domains.
            follow_links: Whether to follow links.
            
        Returns:
            Path to the output file.
        """
        results = self.scrape_urls(urls, allowed_domains, follow_links)
        
        output_path = os.path.join(self.output_dir, output_file)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        return output_path


class AsyncScrapyRunner:
    """Async wrapper for Scrapy runner to use with FastAPI."""
    
    def __init__(
        self,
        output_dir: Optional[str] = None,
        settings: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the async Scrapy runner.
        
        Args:
            output_dir: Directory to store scraped data.
            settings: Optional Scrapy settings override.
        """
        self.output_dir = output_dir or tempfile.mkdtemp()
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        self.settings = settings or {}
    
    async def scrape_url(self, url: str) -> Dict[str, Any]:
        """
        Scrape a single URL asynchronously.
        
        Note: Scrapy is not natively async, this is a simplified implementation.
        For production, consider using Scrapy's CrawlerRunner with Twisted.
        
        Args:
            url: URL to scrape.
            
        Returns:
            Scraped content dictionary.
        """
        import aiohttp
        from bs4 import BeautifulSoup
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")
                
                title = soup.find("title")
                paragraphs = soup.find_all("p")
                
                return {
                    "url": url,
                    "title": title.get_text().strip() if title else "Untitled",
                    "content": " ".join(p.get_text() for p in paragraphs).strip(),
                }
