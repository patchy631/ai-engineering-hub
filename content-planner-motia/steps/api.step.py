from pydantic import BaseModel, HttpUrl

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
    'bodySchema': RequestBody,
    'responseSchema': {
        200: SuccessResponse,
        400: ErrorResponse
    },
    'emits': ['scrape-article'],
    'flows': ['content-generation']
}

async def handler(req, context):
    # Extract request data
    # req = input['req']
    url = req['body']['url']
    
    await context.emit({
        'topic': 'scrape-article',
        'data': {
            'requestId': context.traceId,
            'url': str(url),
            'timestamp': int(__import__('time').time() * 1000)
        }
    })
    
    return {
        'status': 200,
        'body': {
            'message': 'Content generation started',
            'requestId': context.traceId,
            'url': str(url),
            'status': 'processing'
        }
    }