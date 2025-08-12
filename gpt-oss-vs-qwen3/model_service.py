import os
import asyncio
from litellm import acompletion


# Available models
AVAILABLE_MODELS = {
    "GPT-oss-20B": "openrouter/openai/gpt-oss-20b",
    "Qwen3-Thinking": "openrouter/qwen/qwen3-235b-a22b-thinking-2507",
    "GPT-oss-120B": "openrouter/openai/gpt-oss-120b",
}


async def get_model_response_async(prompt: str, model_name: str = "GPT-oss"):
    """
    Get response from reasoning models with reasoning tokens.
    Fetches complete response first, then returns content and reasoning.
    """
    # Use the user prompt directly - let reasoning tokens handle the thinking
    messages = [{"role": "user", "content": prompt}]
    
    # Get model mapping
    model_path = AVAILABLE_MODELS.get(model_name, "openrouter/openai/gpt-oss-20b")

    try:
        # Get complete response with reasoning first
        response = await acompletion(
            model=model_path,
            messages=messages,
            api_key=os.getenv("OPENROUTER_API_KEY"),
            max_tokens=2000,
            reasoning={"effort": "high"}
        )
        
        if not response or not response.choices:
            return {"content": "Error: No response received from model", "reasoning": ""}
        
        message = response.choices[0].message
        content = message.content or ""
        reasoning = ""
        
        # Extract reasoning content
        if hasattr(message, 'reasoning_content') and message.reasoning_content:
            reasoning = message.reasoning_content
        elif hasattr(message, 'reasoning') and message.reasoning:
            reasoning = message.reasoning
        
        return {
            "content": content,
            "reasoning": reasoning
        }
        
    except Exception as e:
        error_msg = f"Error generating response: {str(e)}"
        if "api_key" in str(e).lower():
            error_msg = "Error: Invalid or missing API key. Please check your OPENROUTER_API_KEY configuration."
        elif "quota" in str(e).lower():
            error_msg = "Error: API quota exceeded or rate limit reached. Please try again later."
        
        return {"content": error_msg, "reasoning": ""}


async def get_parallel_responses(prompt: str, model1: str, model2: str):
    """
    Get two parallel responses from selected models for comparison.
    Returns two separate responses to the same prompt.
    """
    # Make two independent calls to get different responses
    response1 = get_model_response_async(prompt, model1)
    response2 = get_model_response_async(prompt, model2)
    
    return response1, response2


def get_all_model_names():
    """Get all available model names."""
    return list(AVAILABLE_MODELS.keys())
