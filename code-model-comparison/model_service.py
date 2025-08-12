import os
import asyncio
from litellm import acompletion
from typing import Dict, Any


# Available models
AVAILABLE_MODELS = {
    "Claude Sonnet 4": "openrouter/anthropic/claude-sonnet-4",
    "Qwen3-Coder": "openrouter/qwen/qwen3-coder",
    "Gemini 2.5 Flash": "openrouter/google/gemini-2.5-flash",
    "GPT-4.1": "openrouter/openai/gpt-4.1",
}


async def get_model_response_async(
    model_name: str, prompt: str, context: Dict[str, Any]
):
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

    messages = [{"role": "user", "content": user_prompt}]

    # Find the model mapping for the given model name
    try:
        model_mapping = get_model_mapping(model_name)
    except ValueError as e:
        yield f"Error: {str(e)}"
        return

    try:
        # Get streaming response from the model using LiteLLM asynchronously.
        response = await acompletion(
            model=model_mapping,
            messages=messages,
            api_key=os.getenv("OPENROUTER_API_KEY"),
            max_tokens=2000,
            stream=True,
        )

        if not response:
            yield "Error: No response received from model"
            return

        async for chunk in response:
            if chunk and hasattr(chunk, "choices") and chunk.choices:
                if chunk.choices[0].delta and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

    except Exception as e:
        error_msg = f"Error generating response: {str(e)}"
        if "api_key" in str(e).lower() or "authentication" in str(e).lower():
            error_msg = "Error: Invalid or missing API key. Please check your OPENROUTER_API_KEY configuration."
        elif "quota" in str(e).lower() or "limit" in str(e).lower():
            error_msg = "Error: API quota exceeded or rate limit reached. Please try again later."
        elif "model" in str(e).lower():
            error_msg = f"Error: Model '{model_name}' is not available or has issues. Please try a different model."

        yield error_msg


async def get_parallel_responses(
    prompt: str, context: Dict[str, Any], model1: str, model2: str
):
    """
    Get parallel responses from two selected models.

    Args:
        prompt: The user prompt
        context: Repository context
        model1: Name of the first model
        model2: Name of the second model

    Returns:
        Tuple of two async generators for the model responses
    """
    gen1 = get_model_response_async(model1, prompt, context)
    gen2 = get_model_response_async(model2, prompt, context)

    return gen1, gen2


def get_model_responses(prompt: str, context: Dict[str, Any], model1: str, model2: str):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(
        get_parallel_responses(prompt, context, model1, model2)
    )


def get_all_model_names():
    """Get all available model names for dropdown selection."""
    try:
        return list(AVAILABLE_MODELS.keys())
    except Exception as e:
        print(f"Error getting model names: {e}")
        return []


def validate_model_name(model_name: str) -> bool:
    """Validate if a model name exists in available models."""
    return model_name in AVAILABLE_MODELS


def get_model_mapping(model_name: str) -> str:
    """Get the model mapping for a given model name."""
    if not validate_model_name(model_name):
        raise ValueError(f"Model '{model_name}' not found in available models")
    return AVAILABLE_MODELS[model_name]
