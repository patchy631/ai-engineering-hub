import os
import asyncio
from litellm import acompletion
from typing import Dict, Any

async def get_model_response_async(model_name: str, prompt: str, context: Dict[str, Any]):
    user_prompt = f"""
    You are an expert code generator. Your task is to generate code based on the following repository context:

    Repository Context:
    {context['content']}

    Instructions:
    1. Generate code that strictly follows the repository's existing patterns and conventions
    2. Use the same coding style, naming conventions, and structure as the codebase
    3. Include clear, concise docstrings and comments explaining key functionality
    4. Ensure the code integrates seamlessly with existing components
    5. Focus on maintainability and readability

    User query:
    {prompt}

    Output only the code implementation without explanations or additional text.
    """

    messages = [
        {"role": "user", "content": user_prompt}
    ]
    
    model_mapping = {
        "o4-mini": "o4-mini",
        "claude-4": "claude-sonnet-4-20250514"
    }
    
    try:
        # Get streaming response from the model using LiteLLM asynchronously.
        response = await acompletion(
            model=model_mapping[model_name],
            messages=messages,
            api_key=os.getenv("OPENAI_API_KEY") if "o4" in model_name else os.getenv("ANTHROPIC_API_KEY"),
            max_tokens=2000,
            stream=True
        )
        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    except Exception as e:
        yield f"Error generating response: {str(e)}"

async def get_parallel_responses(prompt: str, context: Dict[str, Any]):
    claude_gen = get_model_response_async("claude-4", prompt, context)
    openai_gen = get_model_response_async("o4-mini", prompt, context)
    
    return claude_gen, openai_gen

def get_model_responses(prompt: str, context: Dict[str, Any]):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(get_parallel_responses(prompt, context)) 