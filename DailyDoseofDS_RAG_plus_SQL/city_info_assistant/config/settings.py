from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Required API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LLAMACLOUD_API_KEY = os.getenv("LLAMACLOUD_API_KEY")

# Database settings
DATABASE_URL = "sqlite:///database/cities.db"

# Required LlamaCloud settings
LLAMACLOUD_INDEX_NAME = os.getenv("LLAMACLOUD_INDEX_NAME")
LLAMACLOUD_PROJECT_NAME = os.getenv("LLAMACLOUD_PROJECT_NAME")
LLAMACLOUD_ORG_ID = os.getenv("LLAMACLOUD_ORG_ID")

# Optional settings with defaults
LLAMACLOUD_MODEL_NAME = os.getenv("LLAMACLOUD_MODEL_NAME", "gpt-3.5-turbo")
SIMILARITY_TOP_K = int(os.getenv("SIMILARITY_TOP_K", "3"))
WORKFLOW_TIMEOUT = int(os.getenv("WORKFLOW_TIMEOUT", "120")) 