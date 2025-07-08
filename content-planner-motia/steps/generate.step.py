from pydantic import BaseModel, HttpUrl
from typing import Dict, Any
import json
import os
import sys
from datetime import datetime
from openai import OpenAI

# Add the parent directory to the path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.index import config as app_config

class GenerateInput(BaseModel):
    requestId: str
    url: HttpUrl
    title: str
    content: str
    strategy: Dict[str, Any]
    timestamp: int

config = {
    'type': 'event',
    'name': 'GenerateSocialContent',
    'description': 'Generates Twitter and LinkedIn content based on strategy',
    'subscribes': ['generate-content'],
    'emits': ['content-ready'],
    'input': GenerateInput,
    'flows': ['content-generation']
}

# Initialize OpenAI client
openai_client = OpenAI(api_key=app_config.openai['api_key'])

async def handler(input: Dict[str, Any], context):
    context.logger.info(f"✍️ Generating social media content for: {input['title']}")
    
    try:
        # Generate Twitter content
        twitter_prompt_path = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'generate-twitter.txt')
        with open(twitter_prompt_path, 'r', encoding='utf-8') as f:
            twitter_prompt_template = f.read()
        
        # Replace placeholders in Twitter prompt
        twitter_format = 'a Twitter thread (3-5 tweets)' if input['strategy']['twitterStrategy']['format'] == 'thread' else 'a single engaging tweet'
        key_insights = ', '.join(input['strategy']['analysis']['keyInsights'])
        
        twitter_prompt = (twitter_prompt_template
                         .replace('{{title}}', input['title'])
                         .replace('{{strategy}}', json.dumps(input['strategy']['twitterStrategy']))
                         .replace('{{keyInsights}}', key_insights)
                         .replace('{{format}}', twitter_format)
                         .replace('{{targetAudience}}', input['strategy']['analysis']['targetAudience']))
        
        twitter_response = openai_client.chat.completions.create(
            model=app_config.openai['model'],
            messages=[{'role': 'user', 'content': twitter_prompt}],
            temperature=0.8,
            max_tokens=800,
            response_format={'type': 'json_object'}
        )
        
        twitter_content = json.loads(twitter_response.choices[0].message.content)
        
        # Generate LinkedIn content
        linkedin_prompt_path = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'generate-linkedin.txt')
        with open(linkedin_prompt_path, 'r', encoding='utf-8') as f:
            linkedin_prompt_template = f.read()
        
        # Replace placeholders in LinkedIn prompt
        linkedin_prompt = (linkedin_prompt_template
                          .replace('{{title}}', input['title'])
                          .replace('{{strategy}}', json.dumps(input['strategy']['linkedinStrategy']))
                          .replace('{{keyInsights}}', key_insights)
                          .replace('{{targetAudience}}', input['strategy']['analysis']['targetAudience']))
        
        linkedin_response = openai_client.chat.completions.create(
            model=app_config.openai['model'],
            messages=[{'role': 'user', 'content': linkedin_prompt}],
            temperature=0.7,
            max_tokens=1000,
            response_format={'type': 'json_object'}
        )
        
        linkedin_content = json.loads(linkedin_response.choices[0].message.content)
        
        context.logger.info("🎉 Content generated successfully!")
        context.logger.info(f"📱 Twitter: {twitter_content['totalTweets']} tweet(s)")
        context.logger.info(f"💼 LinkedIn: {linkedin_content['characterCount']} characters")
        
        await context.emit({
            'topic': 'content-ready',
            'data': {
                'requestId': input['requestId'],
                'url': str(input['url']),
                'title': input['title'],
                'strategy': input['strategy'],
                'content': {
                    'twitter': twitter_content,
                    'linkedin': linkedin_content
                },
                'metadata': {
                    'generatedAt': datetime.now().isoformat(),
                    'processingTime': int(__import__('time').time() * 1000) - input['timestamp'],
                    'targetAudience': input['strategy']['analysis']['targetAudience']
                }
            }
        })
        
    except Exception as e:
        context.logger.error(f"Content generation failed: {str(e)}")
        raise