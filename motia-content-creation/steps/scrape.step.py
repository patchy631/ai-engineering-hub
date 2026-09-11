import os
from pydantic import BaseModel, HttpUrl
from firecrawl import Firecrawl
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

    firecrawl = Firecrawl(api_key=FIRECRAWL_API_KEY)

    scrapeResult = firecrawl.scrape(input['url'], formats=["markdown"])

    if not hasattr(scrapeResult, 'markdown'):
        raise Exception(f"Firecrawl scraping failed: No content returned")

    content = scrapeResult.markdown or ''
    title = getattr(scrapeResult.metadata, 'title', 'Untitled Article') if hasattr(scrapeResult, 'metadata') else 'Untitled Article'

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