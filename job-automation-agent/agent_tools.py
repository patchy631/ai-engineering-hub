from crewai.tools import tool
import docx
from typing import Any
from job_automation import stagehand_browser_automation


@tool("Read DOCX Resume File")
def read_docx_file(file_path: str) -> str:
    """Reads a DOCX file and returns the full text content.

    This tool is useful for reading and extracting text from DOCX resume files.
    It processes all paragraphs in the document and returns them as a single text string.

    Args:
        file_path: The full path to the DOCX file to read

    Returns:
        The complete text content of the DOCX file, or an error message if reading fails
    """
    try:
        doc = docx.Document(file_path)
        full_text = []
        for paragraph in doc.paragraphs:
            full_text.append(paragraph.text)
        return "\n".join(full_text)
    except Exception as e:
        return f"Error reading docx file: {e}"


@tool("Job Application Automation")
def job_automation(
    website_url: str, profile: dict[str, Any], resume_description: str
) -> str:
    """
    A tool that allows to automate the job application process.
    The tool is used to perform job application tasks powered by Stagehand capabilities.

    Args:
        website_url (str): The URL of the job application page
        profile (dict[str, Any]): The profile of the applicant
        resume_description (str): The resume description for the job application
    """
    return stagehand_browser_automation(website_url, profile, resume_description)
