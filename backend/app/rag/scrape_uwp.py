"""Web scraper for UW-Parkside website."""
from typing import List, Dict, Tuple, Optional
import argparse
import json
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
import httpx
import trafilatura
from collections import deque


class UWPScraper:
    """Scraper for UW-Parkside website content."""

    def __init__(self, max_pages: int = 600, throttle_ms: int = 350):
        self.max_pages = max_pages
        self.throttle_s = throttle_ms / 1000.0
        self.visited_urls = set()
        self.robots_parser = RobotFileParser()
        self.client = httpx.Client(timeout=30.0, follow_redirects=True)

    def setup_robots(self, base_url: str) -> None:
        """Fetch and parse robots.txt."""
        robots_url = urljoin(base_url, "/robots.txt")
        try:
            resp = self.client.get(robots_url)
            if resp.status_code == 200:
                self.robots_parser.parse(resp.text.splitlines())
                print(f"✓ Loaded robots.txt from {robots_url}")
            else:
                print(f"⚠ No robots.txt found at {robots_url}, proceeding without restrictions")
        except Exception as e:
            print(f"⚠ Error fetching robots.txt: {e}")

    def can_fetch(self, url: str) -> bool:
        """Check if URL is allowed by robots.txt."""
        return self.robots_parser.can_fetch("*", url)

    def is_valid_uwp_url(self, url: str) -> bool:
        """Check if URL belongs to uwp.edu domain."""
        parsed = urlparse(url)
        return "uwp.edu" in parsed.netloc

    def normalize_url(self, url: str) -> str:
        """Normalize URL by removing fragments and trailing slashes."""
        parsed = urlparse(url)
        # Remove fragment
        normalized = parsed._replace(fragment="").geturl()
        # Remove trailing slash for consistency
        if normalized.endswith("/") and normalized.count("/") > 3:
            normalized = normalized.rstrip("/")
        return normalized

    def extract_links(self, html: str, base_url: str) -> set[str]:
        """Extract all valid links from HTML content."""
        links = set()
        try:
            from trafilatura import extract
            from lxml import html as lxml_html

            tree = lxml_html.fromstring(html)
            for element in tree.xpath("//a[@href]"):
                href = element.get("href")
                if href:
                    absolute_url = urljoin(base_url, href)
                    normalized = self.normalize_url(absolute_url)
                    if self.is_valid_uwp_url(normalized):
                        links.add(normalized)
        except Exception as e:
            print(f"  Error extracting links: {e}")

        return links

    def scrape_page(self, url: str) -> Optional[dict]:
        """Scrape a single page and extract clean text.

        Returns:
            Dict with url, title, text or None if failed/invalid
        """
        try:
            resp = self.client.get(url, headers={"User-Agent": "UWP-RAG-Bot/1.0"})
            if resp.status_code != 200:
                return None

            # Extract clean text with trafilatura
            extracted = trafilatura.extract(
                resp.text,
                include_links=False,
                include_images=False,
                include_tables=True,
                output_format="txt"
            )

            if not extracted or len(extracted.split()) < 80:
                return None

            # Extract title
            from lxml import html as lxml_html
            tree = lxml_html.fromstring(resp.text)
            title_elements = tree.xpath("//title/text()")
            title = title_elements[0].strip() if title_elements else None

            return {
                "url": url,
                "title": title,
                "text": extracted
            }

        except Exception as e:
            print(f"  Error scraping {url}: {e}")
            return None

    def scrape(self, seed_url: str = "https://www.uwp.edu/") -> List[dict]:
        """Crawl UW-Parkside website starting from seed URL.

        Args:
            seed_url: Starting URL for crawl

        Returns:
            List of scraped page dicts
        """
        print(f"Starting scrape of {seed_url}")
        print(f"Max pages: {self.max_pages}, Throttle: {self.throttle_s}s\n")

        # Setup robots.txt
        self.setup_robots(seed_url)

        # BFS crawl
        queue = deque([self.normalize_url(seed_url)])
        results = []

        while queue and len(results) < self.max_pages:
            url = queue.popleft()

            # Skip if already visited
            if url in self.visited_urls:
                continue

            # Check robots.txt
            if not self.can_fetch(url):
                print(f"✗ Disallowed by robots.txt: {url}")
                self.visited_urls.add(url)
                continue

            self.visited_urls.add(url)
            print(f"[{len(results)+1}/{self.max_pages}] Scraping: {url}")

            # Scrape page
            page_data = self.scrape_page(url)

            if page_data:
                results.append(page_data)

                # Extract links for further crawling
                try:
                    resp = self.client.get(url)
                    links = self.extract_links(resp.text, url)
                    for link in links:
                        if link not in self.visited_urls:
                            queue.append(link)
                except:
                    pass

            # Throttle
            time.sleep(self.throttle_s)

        print(f"\n✓ Scraping complete: {len(results)} pages")
        return results

    def save_to_jsonl(self, data: List[dict], output_path: Path) -> None:
        """Save scraped data to JSONL file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")

        print(f"✓ Saved {len(data)} pages to {output_path}")

    def close(self):
        """Close HTTP client."""
        self.client.close()


def main():
    """CLI entry point for scraping."""
    parser = argparse.ArgumentParser(description="Scrape UW-Parkside website")
    parser.add_argument(
        "--max-pages",
        type=int,
        default=600,
        help="Maximum number of pages to scrape"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/uwp_docs.jsonl"),
        help="Output JSONL file path"
    )
    parser.add_argument(
        "--seed-url",
        type=str,
        default="https://www.uwp.edu/",
        help="Starting URL for crawl"
    )

    args = parser.parse_args()

    scraper = UWPScraper(max_pages=args.max_pages)
    try:
        data = scraper.scrape(seed_url=args.seed_url)
        scraper.save_to_jsonl(data, args.output)
    finally:
        scraper.close()


if __name__ == "__main__":
    main()
