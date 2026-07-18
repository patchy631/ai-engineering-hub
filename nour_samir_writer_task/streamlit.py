
import streamlit as st
from backend import query_backend  # Import backend function

# Streamlit UI
st.title("🔍 AI-Powered City Query Interface")
st.write("Ask about a city's **population, state, or history**, and our AI will find the right source!")

query = st.text_input("Enter your query:")

if st.button("Submit"):
    response_details = query_backend(query)  # Get response dictionary

    # Display the final answer in a readable way
    st.markdown(f"### **Answer:**\n {response_details['final_answer']}")

    # Show details about where the answer came from
    st.markdown(f"##### 📌 **Source:** {response_details['source']}")

    # Show SQL query if applicable
    if "query" in response_details:
        st.markdown(f"##### 📌 **Generated SQL Query:**")
        st.code(response_details["query"], language="sql")

    # Show retrieved documents if applicable
    if "retrieved_documents" in response_details:
        st.markdown(f"##### 📌 **Retrieved Documents:**")
        st.json(response_details["retrieved_documents"])


