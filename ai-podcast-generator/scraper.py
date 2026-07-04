import os
from firecrawl import Firecrawl
from dotenv import load_dotenv

load_dotenv()


class WebScraper:
    def __init__(self):
        self.app = Firecrawl(api_key=os.getenv('FIRECRAWL_API_KEY'))
        
    def scrape(self, url: str) -> str:
        """Scrape content from a given URL."""
        try:
            result = self.app.scrape(url, formats=['markdown'])
            
            # parse correctly
            if isinstance(result, dict):
                content = result.get('markdown', '')
            else:
                content = getattr(result, 'markdown', '')
            
            if not content:
                raise ValueError("No content extracted from URL")
            
            return content
        except Exception as e:
            raise Exception(f"Scraping failed: {str(e)}")