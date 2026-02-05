"""
Multi-Agent Workflow for automating form filling - Generic Form Support

Flow: Document Scanner → Form Data Transformer → Form Filler → Output PDF
"""

import json
import os
import re

from crewai import Agent, Crew, Process, Task
from crewai.flow.flow import Flow, listen, start
from crewai.llm import LLM
from dotenv import load_dotenv

from models import FormFillingFlowState, FormSchema, GenericFormData
from tools import DocumentScanTool, FormFillTool

load_dotenv()


# =============================================================================
# LLM Configuration
# =============================================================================
llm = LLM(
    model="openrouter/minimax/minimax-m2.1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)


# =============================================================================
# Agent Factory Functions (Dynamic based on schema)
# =============================================================================
def create_document_scanner_agent() -> Agent:
    """Create the document scanner agent."""
    return Agent(
        role="Document Scanner Specialist",
        goal="Extract all information from uploaded documents.",
        backstory=(
            "You are an expert document analyst with years of experience in OCR "
            "and data extraction. You specialize in reading documents. "
            "You are meticulous about accuracy and can identify even poorly scanned text."
        ),
        tools=[DocumentScanTool()],
        llm=llm,
    )


def create_form_transformer_agent(schema: FormSchema) -> Agent:
    """Create the form data transformer agent based on schema."""
    field_instructions = schema.to_extraction_prompt()

    return Agent(
        role="Form Data Transformer",
        goal=(
            f"Transform extracted data into the precise form field format for {schema.form_name}. "
            "Map document data to the correct field names with descriptions and properly formatted values."
        ),
        backstory=(
            f"You are a documentation specialist with deep expertise in {schema.form_name}. "
            "You understand exactly how data from source documents maps to each field on the form. "
            "You ensure data is properly formatted and that information is correctly structured.\n\n"
            f"The form has these fields:\n{field_instructions}"
        ),
        llm=llm,
    )


def create_form_filler_agent(schema: FormSchema) -> Agent:
    """Create the form filler agent based on schema."""
    return Agent(
        role="Form Filler",
        goal=(
            f"Accurately map extracted personal data to the correct {schema.form_name} fields "
            "and generate a completed PDF."
        ),
        backstory=(
            "You are a precision-focused form filler. "
            "You excel at matching extracted data to appropriate fields "
            "and ensuring forms are filled correctly."
        ),
        tools=[FormFillTool()],
        llm=llm,
    )


# =============================================================================
# Task Factory Functions (Dynamic based on schema)
# =============================================================================
def create_scan_document_task(agent: Agent) -> Task:
    """Create the document scanning task."""
    return Task(
        description=(
            "Scan and extract ALL information from the document "
            "document file: {document_file}\n\n"
            "Be thorough and accurate. Return all text content found."
        ),
        expected_output="All extracted text content from the document.",
        agent=agent,
    )


def create_transform_data_task(agent: Agent, schema: FormSchema) -> Task:
    """Create the data transformation task based on schema."""
    field_instructions = schema.to_extraction_prompt()

    return Task(
        description=(
            f"Transform the extracted document data into {schema.form_name} field format.\n\n"
            "Input Data:\n{extracted_text}\n\n"
            f"Map the data to these form fields:\n{field_instructions}\n\n"
            "You MUST create a JSON output where each field has:\n"
            "- 'value': The actual data to fill in the field\n"
            "- 'description': A description of what the field represents\n\n"
            "Example format:\n"
            '{"name": {"value": "JOHN DOE", "description": "Name of entity/individual"}, '
            '"address": {"value": "123 Main St", "description": "Street address"}}\n\n'
            "IMPORTANT:\n"
            "- Only include fields that have values from the source document\n"
            "- Skip fields that don't have corresponding data\n"
            "- For SSN/EIN split into separate fields (ssn_1, ssn_2, ssn_3), split the digits appropriately\n"
            "- Strip hyphens from SSN/EIN values - use digits only"
        ),
        expected_output=(
            "A JSON object with form fields mapped correctly. Each field must have "
            "'value' and 'description' keys."
        ),
        agent=agent,
    )


def create_fill_form_task(agent: Agent, schema: FormSchema) -> Task:
    """Create the form filling task based on schema."""
    return Task(
        description=(
            f"Fill out the {schema.form_name} using the provided form data.\n\n"
            "Blank Form Path: {blank_form_path}\n\n"
            "Form Data:\n{form_data}\n\n"
            "Output Path: {output_path}\n\n"
            f"Context for form filling: {schema.context}\n\n"
            "CRITICAL INSTRUCTIONS:\n"
            "1. The form_filler tool uses AI-powered semantic field matching.\n"
            "2. Pass the field_data EXACTLY as provided above - use the semantic field names.\n"
            "3. Each field MUST be a dict with 'value' and 'description' keys.\n"
            "4. Do NOT map to PDF internal field names - use semantic names.\n"
            "5. The tool automatically matches semantic fields to PDF form fields.\n"
            "6. Pass the context parameter to help with semantic matching."
        ),
        expected_output="Confirmation of successful form filling with the path to the completed form.",
        agent=agent,
    )


# =============================================================================
# Generic Form Filling Flow
# =============================================================================
class FormFillingFlow(Flow[FormFillingFlowState]):
    """
    Generic Flow: Document Scanner → Form Data Transformer → Form Filler

    Works with any form type based on the provided FormSchema.
    """

    @start()
    def initialize(self):
        """Validate inputs and initialize workflow."""
        if not self.state.document_file:
            self.state.errors.append("No document file provided")
            return "failed"

        if not self.state.blank_form_path:
            self.state.errors.append("No blank form path provided")
            return "failed"

        if not self.state.form_schema:
            self.state.errors.append("No form schema provided")
            return "failed"

        if not self.state.output_path:
            self.state.output_path = self.state.blank_form_path.replace(
                ".pdf", "_completed.pdf"
            )

        self.state.status = "initialized"
        return "ok"

    @listen(initialize)
    def extract_document_data(self, prev):
        """Extract data from document using OCR."""
        if prev == "failed":
            return "failed"

        scanner_agent = create_document_scanner_agent()
        scan_task = create_scan_document_task(scanner_agent)

        crew = Crew(
            agents=[scanner_agent],
            tasks=[scan_task],
            process=Process.sequential,
            verbose=True,
        )
        result = crew.kickoff(inputs={"document_file": self.state.document_file})

        # Store raw extracted text
        self.state.extracted_text = result.raw if result.raw else ""

        if not self.state.extracted_text:
            self.state.errors.append("No text extracted from document")
            return "failed"

        self.state.status = "data_extracted"
        return "ok"

    @listen(extract_document_data)
    def transform_to_form_data(self, prev):
        """Transform extracted text to form field format using schema."""
        if prev == "failed":
            return "failed"

        if not self.state.extracted_text:
            self.state.errors.append("No extracted text available to transform")
            return "failed"

        schema = self.state.form_schema
        transformer_agent = create_form_transformer_agent(schema)
        transform_task = create_transform_data_task(transformer_agent, schema)

        crew = Crew(
            agents=[transformer_agent],
            tasks=[transform_task],
            process=Process.sequential,
            verbose=True,
        )
        result = crew.kickoff(inputs={"extracted_text": self.state.extracted_text})

        # Parse the result into GenericFormData (handles bool -> string conversion)
        try:
            raw_output = result.raw if result.raw else "{}"
            # Try to extract JSON from the response
            parsed = self._extract_json(raw_output)

            if isinstance(parsed, dict):
                self.state.form_data = GenericFormData.from_dict(parsed)
            else:
                self.state.errors.append("Invalid form data format returned")
                return "failed"

        except json.JSONDecodeError as e:
            self.state.errors.append(f"Failed to parse form data: {e}")
            return "failed"

        self.state.status = "form_data_ready"
        return "ok"

    @listen(transform_to_form_data)
    def fill_form(self, prev):
        """Fill the form using the transformed data."""
        if prev == "failed":
            return "failed"

        if not self.state.form_data:
            self.state.errors.append("Missing form data")
            return "failed"

        schema = self.state.form_schema
        filler_agent = create_form_filler_agent(schema)
        fill_task = create_fill_form_task(filler_agent, schema)

        crew = Crew(
            agents=[filler_agent],
            tasks=[fill_task],
            process=Process.sequential,
            verbose=True,
        )
        crew.kickoff(
            inputs={
                "form_data": json.dumps(
                    self.state.form_data.to_tool_format(), indent=2
                ),
                "blank_form_path": self.state.blank_form_path,
                "output_path": self.state.output_path,
            }
        )

        self.state.completed_form_path = self.state.output_path
        self.state.status = "completed"
        return "ok"

    @listen(fill_form)
    def finalize(self, prev):
        """Return final results with state data for validation."""
        if prev == "failed" or self.state.errors:
            return {"success": False, "errors": self.state.errors}

        # Log state for validation
        print("\n" + "=" * 60)
        print("FLOW STATE OUTPUT")
        print("=" * 60)
        print(f"\nStatus: {self.state.status}")
        print(
            f"Form Type: {self.state.form_schema.form_type if self.state.form_schema else 'N/A'}"
        )

        if self.state.form_data:
            print(
                f"\nForm Data (field_data):\n{json.dumps(self.state.form_data.to_tool_format(), indent=2)}"
            )

        print("=" * 60 + "\n")

        return {
            "success": True,
            "status": self.state.status,
            "form_type": (
                self.state.form_schema.form_type if self.state.form_schema else None
            ),
            "form_data": (
                self.state.form_data.to_tool_format() if self.state.form_data else None
            ),
            "output_path": self.state.completed_form_path,
        }

    def _extract_json(self, text: str) -> dict:
        """Extract JSON from text that may contain markdown code blocks."""
        # Try direct parse first
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try to find JSON in markdown code block
        json_pattern = r"```(?:json)?\s*([\s\S]*?)```"
        matches = re.findall(json_pattern, text)
        for match in matches:
            try:
                return json.loads(match.strip())
            except json.JSONDecodeError:
                continue

        # Try to find raw JSON object
        brace_pattern = r"\{[\s\S]*\}"
        matches = re.findall(brace_pattern, text)
        for match in matches:
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                continue

        raise json.JSONDecodeError("No valid JSON found", text, 0)
