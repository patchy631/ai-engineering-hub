from pydantic import BaseModel, HttpUrl
from typing import Dict, Any
import json
import os
import sys
from openai import OpenAI

# Add the parent directory to the path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.index import config as app_config

class AnalyzeInput(BaseModel):
    requestId: str
    url: HttpUrl
    title: str
    content: str
    timestamp: int

config = {
    'type': 'event',
    'name': 'AnalyzeContent',
    'description': 'Analyzes content and creates strategy for social media',
    'subscribes': ['analyze-content'],
    'emits': ['generate-content'],
    'input': AnalyzeInput,
    'flows': ['content-generation']
}

# Initialize OpenAI client
openai_client = OpenAI(api_key=app_config.openai['api_key'])

async def handler(input: Dict[str, Any], context):
    logger = context.logger
    state = context.state
    emit = context.emit
    trace_id = context.traceId
    
    request_id = input['requestId']
    url = input['url']
    title = input['title']
    content = input['content']
    timestamp = input['timestamp']
    
    logger.info(f"🧠 Analyzing content: {title}")
    
    # Read the prompt template
    prompt_path = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'analyze-content.txt')
    with open(prompt_path, 'r', encoding='utf-8') as f:
        prompt_template = f.read()
    
    # Replace placeholders in the prompt
    prompt = prompt_template.replace('{{title}}', title).replace('{{content}}', content)
    
    try:
        response = openai_client.chat.completions.create(
            model=app_config.openai['model'],
            messages=[{'role': 'user', 'content': prompt}],
            temperature=0.7,
            max_tokens=1500,
            response_format={'type': 'json_object'}
        )
        
        strategy = json.loads(response.choices[0].message.content)
        
        logger.info(f"✅ Strategy created - Target: {strategy['analysis']['targetAudience']}")
        
        await emit({
            'topic': 'generate-content',
            'data': {
                'requestId': request_id,
                'url': str(url),
                'title': title,
                'content': content,
                'strategy': strategy,
                'timestamp': timestamp
            }
        })
        
    except Exception as e:
        logger.error(f"Content analysis failed: {str(e)}")
        raise

