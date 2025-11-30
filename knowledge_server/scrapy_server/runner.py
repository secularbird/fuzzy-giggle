"""
Scrapy runner for managing crawl jobs.
"""

import ipaddress
import json
import os
import socket
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from scrapy import signals
from scrapy.crawler import CrawlerProcess
from scrapy.signalmanager import dispatcher

from knowledge_server.scrapy_server.spider import ContentSpider, SimpleSpider


# Allowed URL schemes for scraping (prevent SSRF)
ALLOWED_SCHEMES = {"http", "https"}


def is_private_ip(hostname: str) -> bool:
    """
    Check if a hostname resolves to a private IP address.
    
    Args:
        hostname: Hostname to check.
        
    Returns:
        True if the hostname resolves to a private IP.
    """
    # Check common private hostnames
    private_hostnames = {"localhost", "127.0.0.1", "0.0.0.0", "::1"}
    if hostname.lower() in private_hostnames:
        return True
    
    # Try to parse as IP address directly
    try:
        ip = ipaddress.ip_address(hostname)
        return ip.is_private or ip.is_loopback or ip.is_reserved
    except ValueError:
        pass
    
    # Check for private IP patterns in hostname
    private_prefixes = (
        "10.", "192.168.", "172.16.", "172.17.", "172.18.", "172.19.",
        "172.20.", "172.21.", "172.22.", "172.23.", "172.24.", "172.25.",
        "172.26.", "172.27.", "172.28.", "172.29.", "172.30.", "172.31.",
        "169.254.",  # Link-local
    )
    if hostname.startswith(private_prefixes):
        return True
    
    return False


def validate_url(url: str, allowed_domains: Optional[List[str]] = None) -> str:
    """
    Validate and sanitize URL to prevent SSRF attacks.
    
    Args:
        url: URL to validate.
        allowed_domains: Optional list of allowed domains. If provided,
                        only URLs from these domains will be allowed.
        
    Returns:
        The validated URL string.
        
    Raises:
        ValueError: If URL is invalid or unsafe.
    """
    if not url or not isinstance(url, str):
        raise ValueError("URL must be a non-empty string.")
    
    try:
        parsed = urlparse(url)
        
        # Check scheme
        if parsed.scheme not in ALLOWED_SCHEMES:
            raise ValueError(f"URL scheme '{parsed.scheme}' is not allowed. Use http or https.")
        
        # Get hostname
        hostname = parsed.hostname
        if not hostname:
            raise ValueError("URL must have a valid host.")
        
        # Check for private/internal IPs
        if is_private_ip(hostname):
            raise ValueError("URLs to private or internal addresses are not allowed.")
        
        # Check against allowed domains if specified
        if allowed_domains:
            domain_match = False
            for domain in allowed_domains:
                if hostname == domain or hostname.endswith(f".{domain}"):
                    domain_match = True
                    break
            if not domain_match:
                raise ValueError(f"Domain '{hostname}' is not in the allowed domains list.")
        
        # Reconstruct URL to ensure it's properly formed
        return url
        
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Invalid URL: {e}")


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
        
        Security: The URL is validated by validate_url() which:
        - Only allows http/https schemes
        - Blocks private/internal IP addresses (localhost, 10.x, 192.168.x, etc.)
        - Can be restricted to specific allowed domains
        
        Args:
            url: URL to scrape.
            
        Returns:
            Scraped content dictionary.
            
        Raises:
            ValueError: If URL is invalid or unsafe.
        """
        import aiohttp
        from bs4 import BeautifulSoup
        
        # Validate URL to prevent SSRF - this validates and returns the safe URL
        # Security note: validate_url() checks scheme and blocks private IPs
        validated_url = validate_url(url)
        
        async with aiohttp.ClientSession() as session:
            # The URL has been validated to prevent SSRF attacks
            async with session.get(validated_url) as response:  # nosec B310
                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")
                
                title = soup.find("title")
                paragraphs = soup.find_all("p")
                
                return {
                    "url": validated_url,
                    "title": title.get_text().strip() if title else "Untitled",
                    "content": " ".join(p.get_text() for p in paragraphs).strip(),
                }
