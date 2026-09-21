import os
from dotenv import load_dotenv, find_dotenv

def load_env():
  _ = load_dotenv(find_dotenv())

def get_mistral_api_key():
  load_env()
  mistral_api_key = os.getenv("MISTRAL_API_KEY")
  return mistral_api_key

def get_openai_api_key():
  load_env()
  openai_api_key = os.getenv("OPENAI_API_KEY")
  return openai_api_key

def get_groq_api_key():
  load_env()
  groq_api_key = os.getenv("GROQ_API_KEY")
  return groq_api_key

def get_serper_api_key():
  load_env()
  serper_api_key = os.getenv("SERPER_API_KEY")
  return serper_api_key