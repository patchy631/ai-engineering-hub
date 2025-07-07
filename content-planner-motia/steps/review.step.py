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

async def handler(input: Dict[str, Any], context):
    logger = context.logger
    state = context.state
    emit = context.emit
    trace_id = context.traceId
    
    request_id = input['requestId']
    title = input['title']
    url = input['url']
    
    logger.info(f"📋 Content ready for review for request: {request_id}")
    
    # Store the content data for later retrieval
    await state.set(f'content-{request_id}', 'content-data', input)
    
    await emit({
        'topic': 'content-stored',
        'data': {
            'requestId': request_id,
            'title': title,
            'url': str(url)
        }
    })

