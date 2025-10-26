import logging
from typing import Dict, Any, Optional
from urllib.parse import urlparse
from datetime import datetime

from firecrawl import Firecrawl

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebScraper:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.app = Firecrawl(api_key=api_key)
        logger.info("WebScraper initialized with Firecrawl")

    def scrape_url(self, url: str, wait_for_results: int = 30) -> Dict[str, Any]:
        """
        Scrape a URL and return the content as text.

        Returns:
            Dict with 'content' (str), 'title' (str), 'url' (str), 'success' (bool)
        """
        if not self._is_valid_url(url):
            raise ValueError(f"Invalid URL format: {url}")

        logger.info(f"Scraping URL: {url}")

        try:
            scrape_params = {
                'formats': ['markdown'],
                'timeout': wait_for_results * 1000
            }

            result = self.app.scrape(url, **scrape_params)

            content = result.markdown
            metadata_dict = result.metadata_dict

            title = metadata_dict.get('title', '') or f"Web Page - {urlparse(url).netloc}"

            logger.info(f"Successfully scraped {url}: {len(content)} characters")

            return {
                'content': content,
                'title': title,
                'url': url,
                'success': True,
                'word_count': len(content.split()) if content else 0,
                'scraped_at': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error scraping URL {url}: {str(e)}")
            return {
                'content': '',
                'title': f"Error - {urlparse(url).netloc}",
                'url': url,
                'success': False,
                'error': str(e),
                'scraped_at': datetime.now().isoformat()
            }

    def _is_valid_url(self, url: str) -> bool:
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
