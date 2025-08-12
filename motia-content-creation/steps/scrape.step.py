import os
from pydantic import BaseModel, HttpUrl
from firecrawl import FirecrawlApp
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

FIRECRAWL_API_KEY = os.getenv('FIRECRAWL_API_KEY')

class ScrapeInput(BaseModel):
    requestId: str
    url: HttpUrl
    timestamp: int

config = {
    'type': 'event',
    'name': 'ScrapeArticle',
    'description': 'Scrapes article content using Firecrawl',
    'subscribes': ['scrape-article'],
    'emits': ['generate-content'],
    'input': ScrapeInput.model_json_schema(),
    'flows': ['content-generation']
}

async def handler(input, context):
    context.logger.info(f"🕷️ Scraping article: {input['url']}")

    app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)

    scrapeResult = app.scrape_url(input['url'])

    if not scrapeResult.success:
        raise Exception(f"Firecrawl scraping failed: {scrapeResult.error}")

    content = scrapeResult.markdown
    title = scrapeResult.metadata.get('title', 'Untitled Article')

    context.logger.info(f"✅ Successfully scraped: {title} ({len(content) if content else 0} characters)")

    await context.emit({
        'topic': 'generate-content',
        'data': {
            'requestId': input['requestId'],
            'url': input['url'],
            'title': title,
            'content': content,
            'timestamp': input['timestamp']
        }
    })