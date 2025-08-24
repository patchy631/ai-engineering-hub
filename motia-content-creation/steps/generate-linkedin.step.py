import os
import json
import ollama
import asyncio
from pydantic import BaseModel, HttpUrl
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'deepseek-r1')

class GenerateInput(BaseModel):
    requestId: str
    url: HttpUrl
    title: str
    content: str
    timestamp: int

config = {
    'type': 'event',
    'name': 'LinkedinGenerate',
    'description': 'Generates LinkedIn content',
    'subscribes': ['generate-content'],
    'emits': ['linkedin-schedule'],
    'input': GenerateInput.model_json_schema(),
    'flows': ['content-generation']
}

async def handler(input, context):
    try:
        with open("prompts/linkedin-prompt.txt", "r", encoding='utf-8') as f:
            linkedinPromptTemplate = f.read()
        
        linkedinPrompt = linkedinPromptTemplate.replace('{{title}}', input['title']).replace('{{content}}', input['content'])

        context.logger.info(f"🔄 LinkedIn content generation started using Ollama model: {OLLAMA_MODEL}...")
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[{'role': 'user', 'content': linkedinPrompt}],
            options={
                'temperature': 0.7,
                'num_predict': 2000
            }
        )  
        
        response_content = response['message']['content']
        context.logger.info(f"Received raw response from Ollama: {response_content[:100]}...")
        
        try:
            linkedin_content = json.loads(response['message']['content'])
        except Exception:
            linkedin_content = {'text': response['message']['content']}
          
        context.logger.info(f"🎉 LinkedIn content generated successfully!")

        await context.emit({
            'topic': 'linkedin-schedule',
            'data': {
                'requestId': input['requestId'],
                'url': input['url'],
                'title': input['title'],
                'content': linkedin_content,
                'generatedAt': datetime.now().isoformat(),
                'originalUrl': input['url']
            }
        })
    except Exception as e:
        context.logger.error(f"❌ Content generation failed: {e}")
        raise e