from pydantic import BaseModel, HttpUrl
from firecrawl import FirecrawlApp
import sys
import os

# Add the parent directory to the path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.index import config as app_config

class ScrapeInput(BaseModel):
    requestId: str
    url: HttpUrl
    timestamp: int

config = {
    'type': 'event',
    'name': 'ScrapeArticle',
    'description': 'Scrapes article content using Firecrawl',
    'subscribes': ['scrape-article'],
    'emits': ['analyze-content'],
    'input': ScrapeInput,
    'flows': ['content-generation']
}

async def handler(input, context):
    context.logger.info(f"🕷️ Scraping article: {input['url']}")
    
    app = FirecrawlApp(api_key=app_config.firecrawl.api_key)

    scrapeResult = await app.scrapeUrl(input['url'], {   
        'formats': ['markdown'],
        'onlyMainContent': True
    })

    if not scrapeResult.success:
        raise Exception(f"Firecrawl scraping failed: {scrapeResult.error}")

    content = scrapeResult.markdown
    title = scrapeResult.metadata.get('title', 'Untitled Article')

    context.logger.info(f"✅ Successfully scraped: {title} ({len(content) if content else 0} characters)")

    await context.emit({
        'topic': 'analyze-content',
        'data': {
            'requestId': input['requestId'],
            'url': str(input['url']),
            'title': title,
            'content': content,
            'timestamp': input['timestamp']
        }
    })