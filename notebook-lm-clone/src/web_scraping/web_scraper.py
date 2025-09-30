import logging
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse, urljoin
import time
from datetime import datetime

from firecrawl import Firecrawl
from src.document_processing.doc_processor import DocumentChunk

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class WebPageData:
    """Represents scraped web page data with additional metadata"""
    url: str
    title: str
    content: str
    metadata: Dict[str, Any]
    success: bool
    error: Optional[str] = None


class WebScraper:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.app = Firecrawl(api_key=api_key)
        
        logger.info("WebScraper initialized with Firecrawl")
    
    def scrape_url(
        self,
        url: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 100,
        wait_for_results: int = 30
    ) -> List[DocumentChunk]:

        if not self._is_valid_url(url):
            raise ValueError(f"Invalid URL format: {url}")
        
        logger.info(f"Scraping URL: {url}")
        
        try:
            scrape_params = {
                'formats': ['markdown', 'html'],
                'timeout': wait_for_results * 1000
            }
            
            result = self.app.scrape(url, **scrape_params)
            page_data = self._process_firecrawl_result(result, url)
            
            chunks = self._create_chunks_from_web_content(
                page_data, 
                chunk_size, 
                chunk_overlap
            )
            
            logger.info(f"Successfully scraped {url}: {len(chunks)} chunks created")
            return chunks
            
        except Exception as e:
            logger.error(f"Error scraping URL {url}: {str(e)}")
            raise
    
    def _process_firecrawl_result(self, result: Dict[str, Any], url: str) -> WebPageData:
        try:
            content = result.markdown
            metadata_dict = result.metadata_dict
            metadata = {
                'scraped_at': datetime.now().isoformat(),
                'original_url': url,
                'title': metadata_dict.get('title', ''),
                'description': metadata_dict.get('description', ''),
                'keywords': metadata_dict.get('keywords', []),
                'language': metadata_dict.get('language', 'en'),
                'word_count': len(content.split()) if content else 0,
                'character_count': len(content) if content else 0,
                'domain': urlparse(url).netloc
            }
            
            return WebPageData(
                url=url,
                title=metadata['title'] or f"Web Page - {metadata['domain']}",
                content=content,
                metadata=metadata,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Error processing Firecrawl result: {str(e)}")
            return WebPageData(
                url=url,
                title=f"Error - {urlparse(url).netloc}",
                content="",
                metadata={'error': str(e), 'scraped_at': datetime.now().isoformat()},
                success=False,
                error=str(e)
            )
    
    def _create_chunks_from_web_content(
        self,
        page_data: WebPageData,
        chunk_size: int,
        chunk_overlap: int
    ) -> List[DocumentChunk]:

        if not page_data.success or not page_data.content.strip():
            logger.warning(f"No content to process for {page_data.url}")
            return []
        
        chunks = []
        content = page_data.content
        start = 0
        chunk_index = 0
        
        while start < len(content):
            end = min(start + chunk_size, len(content))
            if end < len(content):
                last_double_newline = content.rfind('\n\n', start, end)
                if last_double_newline > start + chunk_size * 0.3:
                    end = last_double_newline + 2
                else:
                    last_period = content.rfind('.', start, end)
                    if last_period > start + chunk_size * 0.5:
                        end = last_period + 1
            
            chunk_text = content[start:end].strip()
            
            if chunk_text:
                chunk_metadata = page_data.metadata.copy()
                chunk_metadata.update({
                    'chunk_character_start': start,
                    'chunk_character_end': end - 1,
                    'url_fragment': f"{page_data.url}#chunk-{chunk_index}"
                })
                
                chunk = DocumentChunk(
                    content=chunk_text,
                    source_file=page_data.title,
                    source_type='web',
                    page_number=None,
                    chunk_index=chunk_index,
                    start_char=start,
                    end_char=end-1,
                    metadata=chunk_metadata
                )
                
                chunks.append(chunk)
                chunk_index += 1
            
            start = max(start + chunk_size - chunk_overlap, end)
        
        return chunks
    
    def batch_scrape_urls(
        self,
        urls: List[str],
        chunk_size: int = 1000,
        chunk_overlap: int = 100,
        delay_between_requests: float = 1.0
    ) -> List[List[DocumentChunk]]:
        
        all_chunks = []
        for i, url in enumerate(urls):
            try:
                chunks = self.scrape_url(url, chunk_size, chunk_overlap)
                all_chunks.append(chunks)
                logger.info(f"Successfully scraped {url}: {len(chunks)} chunks")
                
                if i < len(urls) - 1:
                    time.sleep(delay_between_requests)
                    
            except Exception as e:
                logger.error(f"Failed to scrape {url}: {str(e)}")
                all_chunks.append([])
        
        total_chunks = sum(len(chunks) for chunks in all_chunks)
        logger.info(f"Batch scraping complete: {total_chunks} total chunks from {len(urls)} URLs")
        
        return all_chunks
    
    def get_url_preview(self, url: str) -> Dict[str, Any]:
        try:
            result = self.app.scrape(url, **{
                'formats': ['markdown'],
                'timeout': 10000
            })
            
            content = result.markdown
            metadata_dict = result.metadata_dict
            
            preview_info = {
                'url': url,
                'title': metadata_dict.get('title', ''),
                'description': metadata_dict.get('description', ''),
                'word_count': len(content.split()) if content else 0,
                'character_count': len(content) if content else 0,
                'domain': urlparse(url).netloc,
                'content_preview': content[:500] + '...' if len(content) > 500 else content,
                'language': metadata_dict.get('language', 'unknown')
            }
            return preview_info
            
        except Exception as e:
            logger.error(f"Error getting URL preview: {str(e)}")
            return {'error': str(e)}
    
    def _is_valid_url(self, url: str) -> bool:
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False


if __name__ == "__main__":
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        print("Please set FIRECRAWL_API_KEY environment variable")
        exit(1)
    
    scraper = WebScraper(api_key)
    
    try:
        test_url = "https://blog.dailydoseofds.com/p/5-chunking-strategies-for-rag"
        preview = scraper.get_url_preview(test_url)
        print(f"URL Preview: {preview}")
        
        chunks = scraper.scrape_url(test_url)
        print(f"\nScraping Results:")
        print(f"Generated {len(chunks)} chunks")
        
        for i, chunk in enumerate(chunks[:3]):
            print(f"\nChunk {i+1}:")
            print(f"Content: {chunk.content[:200]}...")
            print(f"Source: {chunk.source_file}")
            print(f"URL: {chunk.metadata.get('original_url', 'N/A')}")
            print(f"Citation: [Source: {chunk.source_file}, Type: Web]")
        
        urls = ["https://example.com/page1", "https://example.com/page2"]
        batch_results = scraper.batch_scrape_urls(urls)
        
        total_chunks = sum(len(chunks) for chunks in batch_results)
        print(f"\nBatch Results: {total_chunks} total chunks from {len(urls)} URLs")
        
    except Exception as e:
        print(f"Error in scraping example: {e}")