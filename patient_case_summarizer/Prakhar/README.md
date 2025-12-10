# 🏥 Patient Case Summary AI Agent

This Streamlit application processes patient case documents, extracts medical information, and provides guideline-based recommendations using AI-powered retrieval and LLM models.

---

## 🛠 Setup Instructions

Follow these steps to set up and run the application:

### 1️⃣ **Create a Virtual Environment**
It's recommended to use a virtual environment to manage dependencies.

#### **For macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```
For Windows:
```
python -m venv venv
venv\Scripts\activate
```
### 2️⃣ Install Dependencies

Once the virtual environment is activated, install the required Python packages:
```
pip install -r requirements.txt
```
### 3️⃣ Set Up Environment Variables

Create a .env file in the project directory and add the required API keys:
```
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here
```
### 4️⃣ Run the Application

Launch the Streamlit app using:
```
streamlit run app.py
```
## 📂 Project Structure

📁 Patient Case Summary AI Agent
│── 📂 data_out
│   ├── workflow_output/
│   ├── stored_index/
│── 📂 ref_pdf/             
│── 📂 agent_workflow/      
│── 📜 app.py              
│── 📜 requirements.txt      
│── 📜 .env                 
│── 📜 README.md       


## 🛠 Tech Stack

	•	Streamlit → Interactive UI
	•	LlamaIndex → Document processing & retrieval
	•	Google Gemini API → Embedding generation
	•	Groq API → AI-powered LLM model
	•	Pandas → Data processing

## 🔥 Features

✔ Upload & process patient case documents (JSON/JSONL)

✔ Extract patient info, conditions, medications, encounters

✔ Generate AI-driven guideline recommendations

✔ Uses Google Gemini & Groq LLMs for intelligent retrieval

Note: If you want to add more reference materials for RAG add it in ref_pdf folder. 

## 👨‍💻 Author

Developed by Prakhar Shukla ✨

## 🌟 Contributions

Feel free to contribute! Fork the repo and submit a pull request.
