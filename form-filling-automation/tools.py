"""Tools powered by Datalab SDK for document scanning and form filling."""

import os
from pathlib import Path
from typing import Any, Dict, Type

from crewai.tools import BaseTool
from datalab_sdk import ConvertOptions, DatalabClient, FormFillingOptions
from dotenv import load_dotenv
import nest_asyncio
from pydantic import BaseModel, Field

# Allow nested event loops
nest_asyncio.apply()

load_dotenv()


class DocumentScanInput(BaseModel):
    file_path: str = Field(..., description="Path to user identity document file")


class FormFillInput(BaseModel):
    form_path: str = Field(..., description="Path to the blank form PDF")
    field_data: Dict[str, Any] = Field(..., description="Field data to fill")
    output_path: str = Field(..., description="Path to save the completed form")
    context: str = Field(
        default="Generic form",
        description="Context/description of the form for semantic field matching",
    )


class DocumentScanTool(BaseTool):
    name: str = "document_scanner"
    description: str = "Scans user identity document and extracts text using OCR."
    args_schema: Type[BaseModel] = DocumentScanInput

    def _run(self, file_path: str) -> str:
        # Validate file exists
        if not Path(file_path).exists():
            return f"Error: File not found: {file_path}"

        # Validate API key
        api_key = os.environ.get("DATALAB_API_KEY")
        if not api_key:
            return "Error: DATALAB_API_KEY environment variable not set"

        try:
            client = DatalabClient(api_key=api_key)
            options = ConvertOptions(output_format="markdown", mode="accurate")
            result = client.convert(file_path, options=options)

            if result.success:
                if not result.markdown or result.markdown.strip() == "":
                    return (
                        "Error: OCR returned empty content - document may be unreadable"
                    )
                return result.markdown

            return f"Error: {getattr(result, 'error', 'Unknown OCR error')}"

        except ConnectionError as e:
            return f"Error: Failed to connect to Datalab API: {e}"
        except TimeoutError as e:
            return f"Error: Datalab API request timed out: {e}"
        except Exception as e:
            return f"Error: Unexpected error during document scan: {e}"


class FormFillTool(BaseTool):
    name: str = "form_filler"
    description: str = (
        "Fills PDF form with field data and saves completed form. Accepts dynamic context for any form type."
    )
    args_schema: Type[BaseModel] = FormFillInput

    def _run(
        self,
        form_path: str,
        field_data: Dict[str, Any],
        output_path: str,
        context: str = "Generic form",
    ) -> str:
        # Validate form file exists
        if not Path(form_path).exists():
            return f"Error: Form file not found: {form_path}"

        # Validate field_data is not empty
        if not field_data:
            return "Error: No field data provided to fill the form"

        # Validate API key
        api_key = os.environ.get("DATALAB_API_KEY")
        if not api_key:
            return "Error: DATALAB_API_KEY environment variable not set"

        try:
            client = DatalabClient(api_key=api_key)
            options = FormFillingOptions(
                field_data=field_data,
                confidence_threshold=0.7,
                context=context,  # Dynamic context from schema
                skip_cache=True,
            )
            result = client.fill(form_path, options=options)

            if result.success:
                # Ensure output directory exists
                output_dir = Path(output_path).parent
                output_dir.mkdir(parents=True, exist_ok=True)

                # Verify directory was created
                if not output_dir.exists():
                    return f"Error: Failed to create output directory: {output_dir}"

                result.save_output(output_path)

                # Verify output file was created
                if not Path(output_path).exists():
                    return f"Error: Form was processed but output file was not created: {output_path}"

                # Build diagnostic message
                filled = getattr(result, "fields_filled", [])
                not_found = getattr(result, "fields_not_found", [])
                msg = f"Form filled successfully: {output_path}\n"
                msg += f"Fields filled ({len(filled)}): {filled}\n"
                msg += f"Fields not found ({len(not_found)}): {not_found}"
                return msg

            return f"Error: {getattr(result, 'error', 'Unknown form filling error')}"

        except ConnectionError as e:
            return f"Error: Failed to connect to Datalab API: {e}"
        except TimeoutError as e:
            return f"Error: Datalab API request timed out: {e}"
        except PermissionError as e:
            return f"Error: Permission denied when saving output file: {e}"
        except Exception as e:
            return f"Error: Unexpected error during form filling: {e}"
