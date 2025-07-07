# Python Conversion Guide

This document outlines the conversion of TypeScript steps to Python for the Motia content writing agent.

## Converted Files

### ✅ Converted to Python:
- `api.step.ts` → `api.step.py`
- `scrape.step.ts` → `scrape.step.py`
- `analyze.step.ts` → `analyze.step.py`
- `generate.step.ts` → `generate.step.py`
- `review.step.ts` → `review.step.py`

### ⚠️ Kept as TypeScript (as requested):
- `schedule-api.step.ts` (unchanged)
- `schedule.step.ts` (unchanged)

## Key Changes Made

### 1. Schema Validation
- **Before (Zod)**: `z.object({ url: z.string().url() })`
- **After (Pydantic)**: `class RequestBody(BaseModel): url: HttpUrl`

### 2. Handler Function Format
- **Before (TypeScript)**:
  ```typescript
  export const handler: Handlers['StepName'] = async (input, { emit, logger }) => {
    // logic
  }
  ```
- **After (Python)**:
  ```python
  async def handler(input: Dict[str, Any], context):
      logger = context.logger
      state = context.state
      emit = context.emit
      trace_id = context.traceId
      # logic
  ```

### 3. Input Parameter Access
- **Before**: `input.url` (dot notation)
- **After**: `input['url']` (dictionary access)

### 4. Configuration Import
- **Before**: `const config = require('../config')`
- **After**: `from config.index import config as app_config`

### 5. File Operations
- **Before**: `readFileSync(join(__dirname, '../prompts/file.txt'), 'utf-8')`
- **After**: 
  ```python
  prompt_path = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'file.txt')
  with open(prompt_path, 'r', encoding='utf-8') as f:
      content = f.read()
  ```

### 6. API Client Initialization
- **Before**: `const openai = new OpenAI({ apiKey: config.openai.apiKey })`
- **After**: `openai_client = OpenAI(api_key=app_config.openai['api_key'])`

### 7. HTTP Requests (Firecrawl)
- **Before**: Used `@mendable/firecrawl-js` package
- **After**: Direct HTTP requests using `requests` library

## Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

Required packages:
- `pydantic>=2.0.0` - For schema validation (replaces Zod)
- `openai>=1.0.0` - For OpenAI API calls
- `python-dotenv>=1.0.0` - For environment variable loading
- `requests>=2.28.0` - For HTTP requests (Firecrawl API)

## Configuration

The Python configuration module (`config/index.py`) maintains the same structure as the JavaScript version:

```python
from config.index import config

# Access configuration
api_key = config.openai['api_key']
model = config.openai['model']
```

## Error Handling

All Python steps maintain the same error handling patterns:
- Proper exception catching and re-raising
- Detailed error logging
- Graceful failure handling

## Testing

To test the converted steps:

1. Ensure all environment variables are set (see `.env.example`)
2. Install Python dependencies: `pip install -r requirements.txt`
3. Run the Motia application with the Python steps

## Notes

- All core business logic has been preserved
- Event emission patterns remain identical
- Logging patterns are maintained
- State management operations are unchanged
- The two TypeScript files (`schedule-api.step.ts` and `schedule.step.ts`) remain unchanged as requested

