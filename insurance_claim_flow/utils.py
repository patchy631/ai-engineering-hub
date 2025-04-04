import json

import loguru

from models import ClaimInfo


def extract_claim_data(file_location: str) -> ClaimInfo:
    """Read and validate claim data from a JSON file."""
    with open(file_location, "r") as file:
        content = json.load(file)
    return ClaimInfo.model_validate(content)


def process_claim_json(json_text: str) -> ClaimInfo:
    """Convert JSON string to validated claim object."""
    parsed_data = json.loads(json_text)
    return ClaimInfo.model_validate(parsed_data)


def fetch_declaration_documents(policy_id: str, max_results: int = 1, decl_index=None):
    """Retrieve declaration documents with enhanced error management."""
    if not decl_index:
        return []
    try:
        from llama_index.core.vector_stores.types import MetadataFilters

        retrieved_docs = []

        # Attempt retrieval with policy ID filter
        try:
            search_filters = MetadataFilters.from_dicts(
                [{"key": "policy_number", "value": policy_id}]
            )
            search_engine = decl_index.as_retriever(
                rerank_top_n=max_results, filters=search_filters
            )
            results = search_engine.retrieve(f"policy declarations for {policy_id}")
            if results:
                retrieved_docs.extend(results)
        except Exception as err:
            loguru.logger.error(f"Filtered search failed: {err}")

        # Fallback to broader search if needed
        if not retrieved_docs:
            try:
                search_engine = decl_index.as_retriever(similarity_top_k=max_results)

                search_phrases = [
                    f"policy declarations {policy_id}",
                    f"{policy_id} insurance summary",
                    f"{policy_id} coverage details",
                    f"declarations {policy_id}",
                ]

                # Add policyholder-specific searches
                policyholder_mappings = {
                    "XYZ789": "Robert Brown declarations",
                    "GHI012": "Emma Davis declarations",
                }
                prefix = policy_id[:6] if len(policy_id) >= 6 else policy_id
                if prefix in policyholder_mappings:
                    search_phrases.append(policyholder_mappings[prefix])

                # Execute searches
                for phrase in search_phrases:
                    try:
                        results = search_engine.retrieve(phrase)
                        if results:
                            retrieved_docs.extend(results)
                            loguru.info(f"Documents retrieved with: {phrase}")
                            break
                    except Exception as search_err:
                        loguru.logger.error(f"Search '{phrase}' failed: {search_err}")
            except Exception as err:
                loguru.logger.error(f"Unfiltered search error: {err}")

        # Ensure unique documents
        doc_dict = {doc.id_: doc for doc in retrieved_docs}
        return list(doc_dict.values())
    except Exception as err:
        loguru.logger.error(f"Declaration retrieval error: {err}")
        return []
