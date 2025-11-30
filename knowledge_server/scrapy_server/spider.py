"""
Scrapy spider for web content scraping.
"""

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from typing import Any, Dict, Generator, List, Optional


class ContentSpider(CrawlSpider):
    """Spider for scraping web content."""
    
    name = "content_spider"
    
    def __init__(
        self,
        start_urls: List[str],
        allowed_domains: Optional[List[str]] = None,
        max_depth: int = 2,
        *args,
        **kwargs
    ):
        """
        Initialize the content spider.
        
        Args:
            start_urls: List of URLs to start scraping from.
            allowed_domains: Optional list of allowed domains.
            max_depth: Maximum crawl depth.
        """
        self.start_urls = start_urls
        self.allowed_domains = allowed_domains or []
        self.max_depth = max_depth
        
        # Set up rules for following links
        self.rules = (
            Rule(
                LinkExtractor(allow_domains=self.allowed_domains),
                callback="parse_content",
                follow=True,
            ),
        )
        
        super().__init__(*args, **kwargs)
    
    def parse_content(self, response) -> Generator[Dict[str, Any], None, None]:
        """
        Parse page content.
        
        Args:
            response: Scrapy response object.
            
        Yields:
            Dictionary with scraped content.
        """
        # Extract title
        title = response.css("title::text").get()
        if not title:
            title = response.css("h1::text").get() or "Untitled"
        
        # Extract main content
        paragraphs = response.css("p::text").getall()
        content = " ".join(paragraphs)
        
        # Extract headings
        headings = response.css("h1::text, h2::text, h3::text").getall()
        
        # Extract links
        links = response.css("a::attr(href)").getall()
        
        yield {
            "url": response.url,
            "title": title.strip() if title else "Untitled",
            "content": content.strip(),
            "headings": headings,
            "links": links[:20],  # Limit links
        }


class SimpleSpider(scrapy.Spider):
    """Simple spider for single page scraping."""
    
    name = "simple_spider"
    
    def __init__(self, start_urls: List[str], *args, **kwargs):
        """
        Initialize the simple spider.
        
        Args:
            start_urls: List of URLs to scrape.
        """
        self.start_urls = start_urls
        super().__init__(*args, **kwargs)
    
    def parse(self, response) -> Generator[Dict[str, Any], None, None]:
        """
        Parse page content.
        
        Args:
            response: Scrapy response object.
            
        Yields:
            Dictionary with scraped content.
        """
        title = response.css("title::text").get()
        paragraphs = response.css("p::text").getall()
        
        yield {
            "url": response.url,
            "title": title.strip() if title else "Untitled",
            "content": " ".join(paragraphs).strip(),
        }
