from pydantic import BaseModel, HttpUrl
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
openai_client = OpenAI(api_key=app_config.openai.api_key)

async def handler(input, context):    
    context.logger.info(f"🧠 Analyzing content: {input['title']}")
    
    # Read the prompt template
    prompt_path = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'analyze-content.txt')
    with open(prompt_path, 'r', encoding='utf-8') as f:
        prompt_template = f.read()
    
    # Replace placeholders in the prompt
    prompt = prompt_template.replace('{{title}}', input['title']).replace('{{content}}', input['content'])
    
    try:
        response = openai_client.chat.completions.create(
            model=app_config.openai.model,
            messages=[{'role': 'user', 'content': prompt}],
            temperature=0.7,
            max_tokens=1500,
            response_format={'type': 'json_object'}
        )
        
        strategy = json.loads(response.choices[0].message.content)
        
        context.logger.info(f"✅ Strategy created - Target: {strategy['analysis']['targetAudience']}")
        
        await context.emit({
            'topic': 'generate-content',
            'data': {
                'requestId': input['requestId'],
                'url': str(input['url']),
                'title': input['title'],
                'content': input['content'],
                'strategy': strategy,
                'timestamp': input['timestamp']
            }
        })
        
    except Exception as e:
        context.logger.error(f"Content analysis failed: {str(e)}")
        raise
