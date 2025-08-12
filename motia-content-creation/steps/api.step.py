from pydantic import BaseModel, HttpUrl
from datetime import datetime
import time

class RequestBody(BaseModel):
    url: HttpUrl

class SuccessResponse(BaseModel):
    message: str
    requestId: str
    url: str
    status: str

class ErrorResponse(BaseModel):
    error: str

config = {
    'type': 'api',
    'name': 'ContentGenerationAPI',
    'description': 'Triggers content generation from article URL',
    'path': '/generate-content',
    'method': 'POST',
    'bodySchema': RequestBody.model_json_schema(),
    'responseSchema': {
        200: SuccessResponse.model_json_schema(),
        400: ErrorResponse.model_json_schema()
    },
    'emits': ['scrape-article'],
    'flows': ['content-generation']
}

async def handler(req, context):
    # Extract request data
    url = str(req['body']['url'])

    context.logger.info('🚀 Starting content generation workflow...')
    
    await context.emit({
        'topic': 'scrape-article',
        'data': {
            'requestId': context.trace_id,
            'url': url,
            'timestamp': int(time.time() * 1000)
        }
    })
    
    return {
        'status': 200,
        'body': {
            'message': 'Content generation started',
            'requestId': context.trace_id,
            'url': url,
            'status': 'processing'
        }
    }
