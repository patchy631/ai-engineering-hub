# Patient Case Summary Workflow: Bridging the Gap Between Data and Decision

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE) [![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/) [![LlamaIndex](https://img.shields.io/badge/LlamaIndex-Powered-brightgreen)](https://www.llamaindex.ai/) [![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-red)](https://openai.com/)

**Imagine:** A clinician, overwhelmed by patient data, needs to rapidly understand a patient's history, current status, and recommended care. This project delivers precisely that—a streamlined, agentic workflow that transforms raw patient data into actionable insights.

**This repository showcases a sophisticated system that:**

* **Intelligently Extracts:** Parses complex Synthea-generated patient data (conditions, medications, encounters, etc.) with precision.
* **Dynamically Maps:** Leverages the power of LLMs (specifically GPT-4o) to intelligently associate patient conditions with relevant encounters and medications, creating cohesive "condition bundles."
* **Consults Expert Guidelines:** Seamlessly integrates with LlamaCloud (or a local VectorStoreIndex) to retrieve pertinent medical guidelines (e.g., ADA, NHLBI), ensuring evidence-based recommendations.
* **Generates Actionable Summaries:** Compiles human-readable, clinician-friendly case summaries, highlighting key findings and guideline-driven insights.

**Why This Matters:**

In today's healthcare landscape, data overload is a significant challenge. This workflow empowers clinicians to:

* **Make Faster, More Informed Decisions:** By providing concise, relevant summaries.
* **Improve Patient Care:** By ensuring adherence to best-practice guidelines.
* **Reduce Cognitive Burden:** By automating the time-consuming process of data extraction and analysis.

**Dive In and Explore:**

1.  **Installation:**
    ```bash
    pip install llama-index llama-index-indices-managed-llama-cloud llama-cloud llama-parse
    ```
2.  **Setup:**
    * Obtain Synthea patient data (sample provided in `data/`).
    * (Optional) If using LlamaCloud, configure your API key and upload relevant medical guidelines (PDFs). Otherwise, use `VectorStoreIndex.from_documents` with your own documents.
3.  **Run the Workflow:**
    ```python
    from IPython.display import clear_output
    from llama_index.llms.openai import OpenAI
    # ... (rest of the code from the notebook) ...
    llm = OpenAI(model="gpt-4o")
    workflow = GuidelineRecommendationWorkflow(
        guideline_retriever=retriever,
        llm=llm,
        verbose=True,
        timeout=None,
    )
    handler = workflow.run(patient_json_path="data/almeta_buckridge.json")
    async for event in handler.stream_events():
        if isinstance(event, LogEvent):
            if event.delta:
                print(event.msg, end="")
            else:
                print(event.msg)
    response_dict = await handler
    print(str(response_dict["case_summary"]))
    ```
4.  **Visualize the Workflow:**
    ```python
    from llama_index.utils.workflow import draw_all_possible_flows
    draw_all_possible_flows(GuidelineRecommendationWorkflow, filename="guideline_rec_workflow.html")
    ```

**Key Components:**

* **`parse_synthea_patient()`:** Extracts patient data from JSON.
* **`create_condition_bundles()`:** Maps conditions to encounters/medications using LLMs.
* **`GuidelineRecommendationWorkflow`:** Orchestrates the entire workflow, including guideline retrieval and summary generation.
* **LlamaCloudIndex (or VectorStoreIndex):** Stores and retrieves medical guidelines.
* **GPT-4o:** Powers the LLM-driven tasks.

**Future Enhancements:**

* **Integration with EHR Systems:** To directly process real-world patient data.
* **Enhanced Guideline Coverage:** Expand the index with a broader range of medical guidelines.
* **Personalized Recommendations:** Tailor recommendations based on individual patient preferences and risk factors.
* **Real-time Updates:** Enable dynamic updates to case summaries as new patient data becomes available.

**Contribute:**

We welcome contributions! Feel free to submit pull requests or open issues to suggest improvements or report bugs.

**License:**

This project is licensed under the MIT License.

**Let's work together to revolutionize patient care through the power of AI!**
