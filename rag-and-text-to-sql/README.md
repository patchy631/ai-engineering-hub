<!-- #RAG and Text-to-SQL -->
<a name="readme-top"></a>
<h1 align="center">Multi-Modal Agentic RAG with Dynamic Tool Selection (100% Local)</h1>
  <p align="center">
    The Multi-Modal Agentic RAG is an AI-powered designed to process both structured (SQL-based) and unstructured (document-based) queries. It dynamically selects the appropriate tool based on user input, enabling efficient data retrieval and summarization. 
 <br>
     <br />
    <a href="https://github.com/mayank-cse1/"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://youtu.be/tuBDvjctsco">View Demo</a>
    ·
    <a href="https://github.com/mayank-cse1/ai-engineering-hub/issues">Report Bug</a>
    ·
    <a href="https://typefully.com/t/6FWlbPT">View Tweet</a>
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#prerequisites">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#overview">Overview</a></li>
        <li><a href="#**install-ollama-for-local-llm-access**  ">Installation</a></li>
      </ul>
    </li>
    <li><a href="#to-try-this-sample">Try This Sample</a></li>
    <li><a href="#flow-chart">Workflow Chart</a></li>
    <li><a href="#implementation">Implementation</a></li>
    <li><a href="#demo-video">Demo Video</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>


<!-- ABOUT THE PROJECT -->
## About The Project
![Agentic_multi_modal_RAG_with_tool_selection](https://github.com/user-attachments/assets/5f441987-6d5e-4357-a50e-9207ed6abd41)


The Multi-Modal Agentic RAG is an AI-powered *Hybrid Query Engine* designed to process both structured (SQL-based) and unstructured (document-based) queries. It dynamically selects the appropriate tool based on user input, enabling efficient data retrieval and summarization.  

 🚀 Designed for Users to:
- Efficiently process *multi-modal* data including PDFs, Word Docs, Text, CSV, and Excel.  
- Dynamically *select the right processing method*—SQL, RAG, or a combination of both.  
- Retrieve *instant summarized answers* based on user queries.  
- Integrate seamlessly with various *vector search* and *database management* tools.  


*🔑 Key Features of the Product:*  
- *Intelligent Tool Selection* – Determines whether to use SQL, RAG, or both.  
- *Multi-Modal Processing* – Supports both structured and unstructured data.  
- *Summarized Answers* – Fetches relevant information and presents concise responses.  
- *Adaptive Query Handling* – Adjusts dynamically based on *user-provided data*.  

---
<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Built With

| *Component*       | *Technology Used* |  
|---------------------|--------------------|  
| *LLM Model*      | Meta Llama-3.1 (8B) with Ollama, Meta Llama-3.1 (405B) with SambaNovaCloud API  |  
| *Vector Search*  | Qdrant |  
| *SQL Database*   | SQLAlchemy |  
| *Embeddings*     | HuggingFace Embeddings |  
| *Model Orchestration* | LlamaIndex |


<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Prerequisites

This sample **requires** prerequisites in order to run.

## **1️⃣ Install Ollama for Local LLM Access**  

[Ollama](https://ollama.com) is needed to run *Llama-3.1 (8B)* models locally.  

### **🔹 Steps to Install Ollama**  
#### **🔹 On macOS (via Homebrew)**  
```bash
brew install ollama
```  
#### **🔹 On Linux**  
```bash
curl -fsSL https://ollama.com/install.sh | sh
```  
#### **🔹 On Windows**  
Download and install [Ollama](https://ollama.com/download).  

#### **🔹 Verify Installation**  
```bash
ollama --version
```  
Ensure that the command runs without errors.  

---

## **2️⃣ Sambanova API Key Setup [OPTIONAL]**  

To use *SambaNovaCloud API (405B)* for **remote LLM processing**, store your API key as an environment variable.  

### **🔹 Set Environment Variable**  

#### **🔹 macOS / Linux**  
```bash
export SAMBANOVA_API_KEY="your-api-key-here"
```  
#### **🔹 Windows (PowerShell)**  
```powershell
$env:SAMBANOVA_API_KEY="your-api-key-here"
```  
#### **🔹 Windows (CMD)**  
```cmd
set SAMBANOVA_API_KEY=your-api-key-here
```  
### **🔹 Verify API Key is Set**  
```bash
echo $SAMBANOVA_API_KEY  # For macOS/Linux  
echo %SAMBANOVA_API_KEY%  # For Windows CMD  
$env:SAMBANOVA_API_KEY    # For PowerShell  
```  

---

## **3️⃣ Install Dependencies**  

Ensure **Python 3.8+** is installed, then install the required packages:  

```bash
pip install -r requirements.txt
```  

---

## **4️⃣ Database & Embeddings Setup**  

### **🔹 Install Qdrant for Vector Search**  
```bash
pip install qdrant-client
```  
Alternatively, use **Docker**:  
```bash
docker run -p 6333:6333 qdrant/qdrant
```  

---

## Implementation

![RAG-text-to-sql-demo](https://github.com/user-attachments/assets/80fec8e9-172c-4a5a-8440-4b75708d7c12)
">(<a href="#readme-top">back to top</a>)</p>


## Flow Chart


![RouterOutputAgentWorkflow](https://github.com/user-attachments/assets/87fbf892-dd41-4292-a82f-bbd8c4dbccd0)


## Demo Video

https://github.com/user-attachments/assets/08a2ebea-16ec-4f10-bedf-c60a9effa1ba

👉https://youtu.be/tuBDvjctsco👈


<!-- CONTACT -->
## Contact

Mayank Gupta - [@MayankGuptaCse1](https://twitter.com/MayankGuptacse1) - mayank.guptacse1@gmail.com

Project Link: [https://github.com/mayank-cse1/ai-engineering-hub](https://github.com/mayank-cse1/ai-engineering-hub)

<p align="right">(<a href="#readme-top">back to top</a>)</p>


---

