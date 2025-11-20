import os
import nest_asyncio
from dotenv import load_dotenv
import llama_index.core
from llama_index.llms.openai import OpenAI

# Load environment variables
load_dotenv()

# OpenAI API Key
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PHOENIX_API_KEY = os.getenv('PHOENIX_API_KEY')

# Apply necessary async configurations
nest_asyncio.apply()

# Set up observability and logging
os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = "api_key=4740350e5871ddcaa7a:b0ff61d"
os.environ["PHOENIX_CLIENT_HEADERS"] = "api_key=4740350e5871ddcaa7a:b0ff61d"
os.environ["PHOENIX_COLLECTOR_ENDPOINT"] = "https://app.phoenix.arize.com"

llama_index.core.set_global_handler(
    "arize_phoenix", endpoint="https://llamatrace.com/v1/traces"
)

# Set default LLM model
llama_index.core.Settings.llm = OpenAI("gpt-3.5-turbo")

