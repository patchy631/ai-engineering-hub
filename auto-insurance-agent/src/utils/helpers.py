import json
import os
import logging

logger = logging.getLogger(__name__)

from ..models.schemas import ClaimInfo

def parse_claim(file_path: str) -> ClaimInfo:
    """Parse claim information from a JSON file."""
    with open(file_path, "r") as f:
        data = json.load(f)
    return ClaimInfo.model_validate(data)

def parse_claim_from_json_string(json_string: str) -> ClaimInfo:
    """Parse claim information from a JSON string."""
    data = json.loads(json_string)
    return ClaimInfo.model_validate(data)

def get_declarations_docs(policy_number: str, top_k: int = 1, declarations_index=None):
    """Get declarations retriever with improved error handling and better queries for markdown files."""
    if declarations_index is None:
        return []
    
    try:
        from llama_index.core.vector_stores.types import MetadataFilters
        
        # Try different query approaches to find markdown declaration files
        all_docs = []
        
        # First try with policy number filter
        try:
            filters = MetadataFilters.from_dicts([
                {"key": "policy_number", "value": policy_number}
            ])
            retriever = declarations_index.as_retriever(
                rerank_top_n=top_k,
                filters=filters
            )
            docs = retriever.retrieve(f"declarations page for {policy_number}")
            if docs:
                all_docs.extend(docs)
        except Exception as e:
            logger.error("Error with filtered retrieval: %s", e)
        
        # If no results, try without filters but with more specific queries
        if not all_docs:
            try:
                retriever = declarations_index.as_retriever(similarity_top_k=top_k)
                
                # Try multiple query variations to find markdown declaration files
                queries = [
                    f"declarations page for {policy_number}",
                    f"{policy_number} declarations",
                    f"{policy_number} policy declarations",
                    f"{policy_number} insurance declarations",
                    # Use a dictionary to map policy prefixes to policyholder names
                ]
                
                # Map policy prefixes to policyholder names for more specific queries
                policy_holder_map = {
                    "ABC123": "John Smith declarations",
                    "DEF456": "Alice Johnson declarations"
                }
                
                # Get policy-specific query if available
                policy_prefix = policy_number[:6] if len(policy_number) >= 6 else policy_number
                if policy_prefix in policy_holder_map:
                    queries.append(policy_holder_map[policy_prefix])
                
                # Filter out None values
                queries = [q for q in queries if q]
                
                for query in queries:
                    try:
                        docs = retriever.retrieve(query)
                        if docs:
                            all_docs.extend(docs)
                            logger.info("Found docs with query: %s", query)
                            break  # Stop once we find documents
                    except Exception as query_e:
                        logger.error("Error with query '%s': %s", query, query_e)
            except Exception as e:
                logger.error("Error with unfiltered retrieval: %s", e)
        
        # Return unique documents
        unique_docs = {}
        for doc in all_docs:
            unique_docs[doc.id_] = doc
        
        return list(unique_docs.values())
    except Exception as e:
        # Log the error but don't crash
        logger.error("Error retrieving declarations: %s", e)
        return []

def load_policy_file_mapping():
    """Load policy to file mapping from configuration file or database."""
    # Default mapping in case the config file is not available
    default_mapping = {
        "POLICY-ABC123": "data/john-declarations.md",
        "POLICY-DEF456": "data/alice-declarations.md"
    }
    
    try:
        # Try to load from a configuration file
        config_path = "config/policy_mappings.json"
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                return json.load(f)
        return default_mapping
    except Exception as e:
        logger.error("Error loading policy file mapping: %s", e)
        return default_mapping

def get_local_declaration_file(policy_number: str):
    """Check for local declaration files in the data directory."""
    # Load mapping from a configuration file or database
    policy_file_map = load_policy_file_mapping()
    
    # Check if we have a mapping for this policy number
    if policy_number in policy_file_map:
        file_path = policy_file_map[policy_number]
        try:
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    return f.read()
        except Exception as e:
            logger.error("Error reading local declaration file: %s", e)
    
    # Also try a more general pattern search in the data directory
    try:
        data_dir = "data"
        if os.path.exists(data_dir) and os.path.isdir(data_dir):
            for filename in os.listdir(data_dir):
                if policy_number.lower() in filename.lower() and filename.endswith((".md", ".txt")):
                    file_path = os.path.join(data_dir, filename)
                    with open(file_path, "r") as f:
                        return f.read()
    except Exception as e:
        logger.error("Error searching for declaration files: %s", e)
    
    return None

def generate_workflow_visualization():
    """Generate workflow visualization HTML."""
    from llama_index.utils.workflow import draw_all_possible_flows
    from ..workflow.workflow import AutoInsuranceWorkflow
    
    # Generate the visualization HTML
    html_file = "auto_insurance_workflow.html"
    draw_all_possible_flows(AutoInsuranceWorkflow, filename=html_file)
    
    # Read the generated HTML file
    with open(html_file, "r") as f:
        html_content = f.read()
    
    return html_content 
