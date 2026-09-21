import os 
from llama_index.indices.managed.llama_cloud import LlamaCloudIndex
from llama_cloud.client import LlamaCloud
from llama_index.llms.ollama import Ollama

from dotenv import load_dotenv

load_dotenv()

# Llama cloud 
llama_cloud_api_key = os.getenv("LLAMA_CLOUD_API_KEY")
org_id = os.getenv("ORGANIZATION_ID")

if not llama_cloud_api_key:
    raise ValueError("LLAMA_CLOUD_API_KEY environment variable is required")

if not org_id:
    raise ValueError("ORGANIZATION_ID environment variable is required")

def policy_index(): 
    index = LlamaCloudIndex(
        name="auto_insurance_policy", 
        project_name="ddods",
        organization_id=org_id,
        api_key=llama_cloud_api_key
    )
    return index 

def llama_client(): 
    client = LlamaCloud(
        base_url="https://api.cloud.llamaindex.ai",
        token = llama_cloud_api_key
    )
    return client 

def ollama_llm():
    llm = Ollama(model="llama3.1:latest", 
                 request_timeout=360.0)
    return llm 


def get_opik_tracker(): 
    """Get opik tracing api key and opik worspace name 
    Returns:
        Tuple[str, str]: A tuple containing (api_key, workspace_name)
    """
    api_key = os.getenv("OPIK_API_KEY")
    opik_workspace = os.getenv("OPIK_WORKSPACE")
    project_name = os.getenv("OPIK_PROJECT_NAME")
    if not api_key:
        raise ValueError(
            "OPIK API KEY not set visit https://www.comet.com/opik to set" )
    return api_key, opik_workspace, project_name
