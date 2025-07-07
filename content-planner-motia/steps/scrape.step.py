from pydantic import BaseModel, HttpUrl
from typing import Dict, Any
import requests
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

async def handler(input: Dict[str, Any], context):
    logger = context.logger
    state = context.state
    emit = context.emit
    trace_id = context.traceId
    
    url = input['url']
    request_id = input['requestId']
    timestamp = input['timestamp']
    
    logger.info(f"🕷️ Scraping article: {url}")
    
    # Use Firecrawl API directly via HTTP requests
    firecrawl_url = "https://api.firecrawl.dev/v1/scrape"
    headers = {
        'Authorization': f'Bearer {app_config.firecrawl["api_key"]}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'url': str(url),
        'formats': ['markdown'],
        'onlyMainContent': True
    }
    
    try:
        response = requests.post(firecrawl_url, json=payload, headers=headers)
        response.raise_for_status()
        scrape_result = response.json()
        
        if not scrape_result.get('success'):
            raise Exception(f"Firecrawl scraping failed: {scrape_result.get('error', 'Unknown error')}")
        
        content = scrape_result.get('data', {}).get('markdown', '')
        title = scrape_result.get('data', {}).get('metadata', {}).get('title', 'Untitled Article')
        
        logger.info(f"✅ Successfully scraped: {title} ({len(content) if content else 0} characters)")
        
        await emit({
            'topic': 'analyze-content',
            'data': {
                'requestId': request_id,
                'url': str(url),
                'title': title,
                'content': content,
                'timestamp': timestamp
            }
        })
        
    except requests.exceptions.RequestException as e:
        logger.error(f"HTTP request failed: {str(e)}")
        raise Exception(f"Firecrawl scraping failed: {str(e)}")
    except Exception as e:
        logger.error(f"Scraping failed: {str(e)}")
        raise

