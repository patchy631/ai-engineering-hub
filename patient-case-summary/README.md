# Patient Case Summary

![Image](https://github.com/user-attachments/assets/2a6377b2-405e-42bb-9538-f06cf7ea6b50)

This project provides a workflow for generating patient case summaries using a combination of patient data and medical guidelines. The workflow is implemented using LlamaIndex as agentic framework, OpenAI's `gpt-4o-mini` model as LLM and Streamlit for the user interface.

## Project Structure

```
.env
.gitignore
.python-version
app.py
diagram.excalidraw
pyproject.toml
README.md
uv.lock
.streamlit/
    config.toml
data/
    almeta_buckridge.json
```

## Setup Instructions

1. **Create virtual environment and install dependencies:**

    ```bash
    uv sync
    source .venv/bin/activate
    ```

4. **Set up environment variables:**

    Create a `.env` file in the root directory and add the following environment variables:

    ```env
    LLAMA_CLOUD_API_KEY=<your_llama_cloud_api_key>
    ORGANIZATION_ID=<your_organization_id>
    OPENAI_API_KEY=<your_openai_api_key>
    ```

5. **Run the Streamlit application:**

    ```bash
    uv run streamlit run app.py
    ```

## Usage Instructions

1. **Upload a Patient JSON File:**

    - Open the Streamlit application in your browser.
    - Use the file uploader to upload a patient JSON file located in the folder `data`.

2. **Run the Patient Case Workflow:**

    - After uploading the file, click the "Run Patient Case Workflow" button.
    - The application will process the file and display the results.

## Project Components

- **app.py:** Main application file containing the workflow and Streamlit UI.
- **data/:** Directory containing sample patient data files.
- **data_out/:** Directory where workflow output files are saved.
- **.streamlit/:** Directory containing Streamlit configuration files.

## Workflow Details

The workflow involves the following steps:

1. **Parse Patient Info:** Extract patient information from the uploaded JSON file.
2. **Create Condition Bundles:** Group conditions with relevant encounters and medications.
3. **Generate Guideline Queries:** Formulate queries to retrieve relevant medical guidelines.
4. **Match Guidelines:** Retrieve and match guidelines to the patient's conditions.
5. **Generate Case Summary:** Produce a case summary integrating all the information.

