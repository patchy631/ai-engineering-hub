import requests
from llama_index.core import Settings
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama

def is_ollama_running(ollama_base_url="http://localhost:11434"):
    """
    Check if Ollama server is running by testing the /api/tags endpoint.
    """
    try:
        response = requests.get(f"{ollama_base_url}/api/tags")
        return (response.status_code == 200)
    except:
        return False

def get_available_models(ollama_base_url="http://localhost:11434"):
    """
    Fetch available models from the Ollama server.
    """
    try:
        response = requests.get(f"{ollama_base_url}/api/tags")
        if response.status_code == 200:
            models = response.json().get("models", [])
            return [model.get("name") for model in models]
        return ["No models found"]
    except Exception as e:
        return [f"Error getting models: {str(e)}"]

def get_available_embedding_models(ollama_base_url="http://localhost:11434"):
    """
    Fetch available embedding models (filtered) from the Ollama server.
    If none explicitly match embedding-related naming, return all.
    """
    try:
        response = requests.get(f"{ollama_base_url}/api/tags")
        if response.status_code == 200:
            models = response.json().get("models", [])
            embedding_models = [
                model.get("name") for model in models 
                if any(name in model.get("name").lower() for name in ["embed", "nomic", "all-minilm"])
            ]
            if not embedding_models:
                return [model.get("name") for model in models]
            return embedding_models
        return ["all-minilm"]
    except Exception as e:
        return [f"Error getting embedding models: {str(e)}"]

def load_models(
    temperature: float, 
    max_tokens: int, 
    ollama_base_url: str, 
    model_name: str, 
    embed_model_name: str
):
    """
    Load the specified LLM and Embedding model from Ollama and assign them 
    to llama_index.core.Settings.
    """
    if not is_ollama_running(ollama_base_url):
        raise RuntimeError("Ollama is not running. Please start Ollama server first.")
    
    llm = Ollama(
        model=model_name,
        base_url=ollama_base_url,
        request_timeout=120.0,
        temperature=temperature,
        additional_kwargs={"num_predict": max_tokens}
    )
    
    embed_model = OllamaEmbedding(
        model_name=embed_model_name,
        base_url=ollama_base_url,
        embed_batch_size=10
    )
    
    Settings.llm = llm
    Settings.embed_model = embed_model
    
    return llm, embed_model