import streamlit as st
from PIL import Image
import asyncio
from agent import wf  # Import the initialized workflow agent
from query_processor import QueryProcessor

# Initialize the query processor
processor = QueryProcessor()

async def get_response_async(query):
    return await wf.run(message=query)



def main():
    st.set_page_config(page_title="Advanced RAG: RAG + Text-to-SQL", layout="wide")
    
    # Title and Description
    st.markdown(
    """
    <h1 style='text-align: center;'>
        🤖 <span style='color:#FF4B4B;'>Advanced RAG</span>: 
        <span style='color:#4B8BFF;'>Text-to-SQL</span>
    </h1>
    <h3 style='text-align: center;'>🧠 Powered by OpenAI & 🦙 Llama Cloud</h3>
    """,
    unsafe_allow_html=True
)
    
    st.markdown("""
    This application processes user queries by intelligently routing them to either
    a Text-to-SQL module for structured data retrieval or a RAG-based retrieval system
    for knowledge base queries. The response is synthesized using an LLM.
    """)
    
    # Sidebar for User Input
    st.sidebar.header("User Query Input")
    user_query = st.sidebar.text_area("Enter your query:")
    
    
    response = ""
    if st.sidebar.button("Submit Query"):
        if user_query:
            with st.spinner("Processing your query..."):
                response = processor.get_response(user_query)
        else:
            st.warning("Please enter a query before submitting.")
    
    # Display Response
    st.subheader("Response")
    st.info(response if response else "Awaiting query submission...")
    
    # Displaying the Flowchart (Optional)
    st.subheader("Processing Flowchart")
    image = Image.open("images/textTosql.png")  # Load uploaded image
    st.image(image, caption="System Workflow", use_column_width=True)
    
    # Footer
    st.markdown("""
    **Built using Streamlit** | Integrates RAG with Text-to-SQL for intelligent query handling.
    """)
    
if __name__ == "__main__":
    main()