# 🚀 Intelligent City Data Search Engine  

## 📌 Overview  
This project is an **AI-powered city data search engine** that allows users to:  
✅ Retrieve population data from a structured SQLite database.  
✅ Search city-related documents efficiently.  
✅ Answer complex city-related queries using **Google Gemini AI** for better understanding.  

It utilizes **Google Gemini, LlamaIndex, and SQLite** to enable intelligent search and data retrieval.  

---

## 🏗️ Architecture & Workflow  
Here’s how the system works:  

1️⃣ The **structured database** (SQLite) stores city data like population statistics.  
2️⃣ A user enters a query, which gets processed by **LlamaIndex**.  
3️⃣ If the query requires factual data, it fetches it from SQLite.  
4️⃣ If the query is more complex, it is sent to **Google Gemini AI** for interpretation.  
5️⃣ The response is refined and returned to the user.  

---

## 🖥️ Demo  
📌 **A quick look at what we built!**  
🔹 Retrieve structured city data 📊  
🔹 Search city documents intelligently 🔍  
🔹 Answer complex city-related queries 💡  

Check out a demo Video and screenshot below 👇  

![🎥 Video Demo](https://bit.ly/DDODS)
![Demo Screenshot](/demo_rag.png)

---

## ⚙️ Tech Stack  
🔹 **Google Gemini AI** → Provides AI-powered query understanding.  
🔹 **LlamaIndex** → Helps manage and retrieve relevant documents.  
🔹 **SQLite** → Stores structured city population & statistical data.  
🔹 **Python** → Backend development.  

---

## 🚀 Installation & Setup  

### **Step 1: Clone the Repository**  
```bash
git clone <https://github.com/>
cd <your-repo-name>

### **Step 2: Create a Virtual Environment**   
```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

### **Step 3: Install Dependencies**
```bash
pip install -r requirements.txt

### **Step 4: Run the Application**
```bash
streamlit app.py

This will launch the application and allow you to start querying city data!

## Project Structure 📂

📂 my-project
│── 📄 app.py            # Main application script
│── 📄 workflow.py       # Workflow script
│── 📄 requirements.txt  # Dependencies
│── 📄 README.md         # Project documentation

## ❓ FAQs  

### **1️⃣ How does the search work?**  
The app first checks structured data (SQLite).  
If no match is found, it searches indexed documents using LlamaIndex.  
If further interpretation is needed, the query is sent to Google Gemini AI.  
The final response is returned to the user.  

### **2️⃣ Can I add more data?**  
Yes! You can update the SQLite database or index new documents into the system.  

---

## 📢 Contribution  
Feel free to submit pull requests or open issues for improvements!  

---

## 📌 Author  
👤 **Mohamed Kayser**  
🔗 [GitHub](https://github.com/mohammedkayser) | [LinkedIn](https://www.linkedin.com/in/mohammedkayser/)  

