# Patient Summary Generation using LLMs

## 📌 Project Overview
This project demonstrates how to generate structured **patient summaries** using an **LLM (Large Language Model)**. The system extracts relevant details from raw medical records and transforms them into concise, clinically useful summaries.

Due to **API cost limitations**, the demo includes a **hardcoded output** to illustrate how the system works.

---

## ⚙️ Setup Instructions

### **1️⃣ Clone the Repository**
```bash
git clone https://github.com/patchy631/ai-engineering-hub.git
cd ai-engineering-hub/patient-summary-llm
```

### **2️⃣ Install Dependencies**
Ensure you have Python 3.8+ installed. Then, install the required libraries:
```bash
pip install -r requirements.txt
```

### **3️⃣ Run the Application**
```bash
streamlit run app.py
```
This will showcase a **demo of the output**, which is currently **hardcoded** due to API restrictions.

---

## 🚀 How It Works

### **🔹 Input: Raw Patient Record**
The system takes **unstructured medical data** and formats it into a structured prompt for the LLM.

### **🔹 Processing: LLM Summarization**
The model is designed to extract key details such as:
- **Patient Demographics** (Name, Age, Gender)
- **Medical History**
- **Current Medications**
- **Diagnosis & Treatment Plans**

### **🔹 Output: Structured Patient Summary**
The LLM generates a **concise, clinically relevant** summary.

**Example:**
```plaintext
Patient: John Doe, 45M
Diagnosis: Type 2 Diabetes, Hypertension
Medications: Metformin, Lisinopril
Treatment Plan: Lifestyle changes, Medication adherence
```

---

## ⚠️ Note on Hardcoded Output
Due to **API cost constraints**, the output shown in this demo is **hardcoded**. However, the real implementation would:
- **Call an LLM API (e.g., OpenAI, Cohere, or Hugging Face)**
- **Process real patient records dynamically**

If you want to integrate with an **LLM API**, modify `app.py` and add your API key.

---

## 📌 Next Steps
- 🔹 Implement API calls for **real-time LLM processing**
- 🔹 Improve **data privacy** and **HIPAA compliance**
- 🔹 Optimize **prompt engineering** for better summaries

---

## 🛠 Contributing
To contribute, create a **Pull Request (PR)** with your updates:
```bash
git checkout -b feature-branch
git add .
git commit -m "Added feature"
git push origin feature-branch
```
Then, open a PR on GitHub.

---

## 🔗 Follow for More
If you found this useful, follow for more insights on **LLMs, AI, and NLP**! 🚀

