"""Main entry point for the generic form filling workflow."""

from typing import Any, Dict, Optional

from flow import FormFillingFlow
from models import load_schema


def run_form_flow(
    document_file: str,
    blank_form_path: str,
    schema_path: str,
    output_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Run the generic form filling workflow.

    Args:
        document_file: Path to source document file (e.g., identity document)
        blank_form_path: Path to the blank form PDF to fill
        schema_path: Path to the form schema YAML/JSON file
        output_path: Optional path for the completed form

    Returns:
        Dictionary with workflow results including:
        - success: bool
        - status: str
        - form_type: str
        - form_data: dict (the field_data used for filling)
        - output_path: str (path to completed PDF)
        - errors: list (if failed)
    """
    # Load the form schema
    schema = load_schema(schema_path)

    # Create and configure the flow
    flow = FormFillingFlow()
    flow.state.document_file = document_file
    flow.state.blank_form_path = blank_form_path
    flow.state.form_schema = schema
    flow.state.output_path = output_path or ""

    return flow.kickoff()


# Backward compatibility alias
run_tax_form_flow = run_form_flow


if __name__ == "__main__":
    # Example usage with W-9 form
    document_file = "documents/user-identity.pdf"
    blank_form_path = "documents/fw9.pdf"
    schema_path = "schemas/w9.yaml"
    output_path = "output/fw9_completed.pdf"

    result = run_form_flow(
        document_file=document_file,
        blank_form_path=blank_form_path,
        schema_path=schema_path,
        output_path=output_path,
    )
    print(f"\nResult: {result}")
