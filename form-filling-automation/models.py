"""Pydantic Models for Structured Data - Generic Form Support"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field
import yaml


# =============================================================================
# Generic Form Schema Models
# =============================================================================
class FormField(BaseModel):
    """Single field definition for any form schema."""

    name: str = Field(..., description="Field key (e.g., 'ssn_1', 'name')")
    description: str = Field(..., description="What to extract/fill for this field")
    required: bool = Field(default=True, description="Whether field is required")
    validation_pattern: Optional[str] = Field(
        default=None, description="Optional regex pattern for validation"
    )


class FormSchema(BaseModel):
    """Generic form schema - loaded from YAML/JSON config."""

    form_type: str = Field(
        ..., description="Form identifier (e.g., 'w9', '1099', 'i9')"
    )
    form_name: str = Field(..., description="Human-readable form name")
    context: str = Field(
        ..., description="Description/context for the form filling API"
    )
    fields: List[FormField] = Field(..., description="List of form fields")

    @classmethod
    def from_yaml(cls, path: str) -> "FormSchema":
        """Load form schema from a YAML file."""
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return cls(**data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FormSchema":
        """Load form schema from a dictionary."""
        return cls(**data)

    def get_field_names(self) -> List[str]:
        """Get list of all field names."""
        return [f.name for f in self.fields]

    def get_required_fields(self) -> List[str]:
        """Get list of required field names."""
        return [f.name for f in self.fields if f.required]

    def get_field_descriptions(self) -> Dict[str, str]:
        """Get mapping of field names to descriptions."""
        return {f.name: f.description for f in self.fields}

    def to_extraction_prompt(self) -> str:
        """Generate field extraction instructions for agents."""
        lines = []
        for f in self.fields:
            req = "(required)" if f.required else "(optional)"
            lines.append(f"- {f.name}: {f.description} {req}")
        return "\n".join(lines)


class GenericFormData(BaseModel):
    """Generic extracted/transformed form data - works with any form schema."""

    field_data: Dict[str, Dict[str, str]] = Field(
        default_factory=dict,
        description="Form data: {field_name: {'value': str, 'description': str}}",
    )

    def to_tool_format(self) -> Dict[str, Dict[str, str]]:
        """Convert to format expected by TaxFormFillTool."""
        return self.field_data

    def get_value(self, field_name: str) -> Optional[str]:
        """Get value for a specific field."""
        if field_name in self.field_data:
            return self.field_data[field_name].get("value")
        return None

    def set_field(self, name: str, value: str, description: str) -> None:
        """Set a field value with description."""
        self.field_data[name] = {"value": value, "description": description}

    @staticmethod
    def _to_string(value: Any) -> str:
        """Convert any value to string, handling booleans specially."""
        if isinstance(value, bool):
            return "Yes" if value else "No"
        if value is None:
            return ""
        return str(value)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GenericFormData":
        """Create from a dictionary, converting non-string values to strings."""
        normalized = {}
        for field_name, field_info in data.items():
            if isinstance(field_info, dict):
                normalized[field_name] = {
                    "value": cls._to_string(field_info.get("value", "")),
                    "description": cls._to_string(field_info.get("description", "")),
                }
        return cls(field_data=normalized)

    def validate_against_schema(self, schema: FormSchema) -> List[str]:
        """Validate form data against schema, return list of errors."""
        errors = []
        for field in schema.fields:
            if field.required:
                if field.name not in self.field_data:
                    errors.append(f"Missing required field: {field.name}")
                elif not self.field_data[field.name].get("value"):
                    errors.append(f"Empty value for required field: {field.name}")
        return errors


# =============================================================================
# Flow State Model
# =============================================================================
class FormFillingFlowState(BaseModel):
    """State management for the generic form filling flow."""

    # Input paths
    document_file: str = ""
    blank_form_path: str = ""
    output_path: str = ""

    # Schema (loaded from config)
    form_schema: Optional[FormSchema] = None

    # Extracted and transformed data
    extracted_text: str = ""  # Raw OCR output
    form_data: Optional[GenericFormData] = None  # Transformed field data

    # Output
    completed_form_path: str = ""
    status: str = "pending"
    errors: List[str] = Field(default_factory=list)


# =============================================================================
# Helper Functions
# =============================================================================
def load_schema(schema_path: str) -> FormSchema:
    """Load a form schema from file path."""
    path = Path(schema_path)
    if not path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    if path.suffix in (".yaml", ".yml"):
        return FormSchema.from_yaml(schema_path)
    elif path.suffix == ".json":
        import json

        with open(schema_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return FormSchema.from_dict(data)
    else:
        raise ValueError(f"Unsupported schema format: {path.suffix}")


def list_available_schemas(schemas_dir: str = "schemas") -> List[Dict[str, str]]:
    """List all available form schemas in the schemas directory."""
    schemas = []
    schemas_path = Path(schemas_dir)

    if not schemas_path.exists():
        return schemas

    for file in schemas_path.glob("*.yaml"):
        try:
            schema = FormSchema.from_yaml(str(file))
            schemas.append(
                {
                    "file": file.name,
                    "path": str(file),
                    "form_type": schema.form_type,
                    "form_name": schema.form_name,
                }
            )
        except Exception:
            continue

    for file in schemas_path.glob("*.yml"):
        try:
            schema = FormSchema.from_yaml(str(file))
            schemas.append(
                {
                    "file": file.name,
                    "path": str(file),
                    "form_type": schema.form_type,
                    "form_name": schema.form_name,
                }
            )
        except Exception:
            continue

    return schemas
