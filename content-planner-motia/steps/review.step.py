from pydantic import BaseModel, HttpUrl
from typing import Dict, Any

class ContentData(BaseModel):
    twitter: Dict[str, Any]
    linkedin: Dict[str, Any]

class ReviewInput(BaseModel):
    requestId: str
    url: HttpUrl
    title: str
    strategy: Dict[str, Any]
    content: ContentData
    metadata: Dict[str, Any]

config = {
    'type': 'event',
    'name': 'ContentReview',
    'description': 'Stores generated content in the state',
    'subscribes': ['content-ready'],
    'emits': ['content-stored'],
    'input': ReviewInput,
    'flows': ['content-generation']
}

async def handler(input, context):
    context.logger.info(f"📋 Content ready for review for request: {input['requestId']}")
    
    # Store the content data for later retrieval
    await context.state.set(f'content-{input['requestId']}', 'content-data', input)
    
    await context.emit({
        'topic': 'content-stored',
        'data': {
            'requestId': input['requestId'],
            'title': input['title'],
            'url': str(input['url'])
        }
    })