import streamlit as st
import os
import gc
from firecrawl import FirecrawlApp
from dotenv import load_dotenv
import time
import pandas as pd
from typing import Dict, Any
import base64
from pydantic import BaseModel, Field
import inspect


load_dotenv()
firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")

@st.cache_resource
def load_app():
    app = FirecrawlApp(api_key=firecrawl_api_key)
    return app

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "schema_fields" not in st.session_state:
    st.session_state.schema_fields = [{"name": "", "type": "str"}]

def reset_chat():
    st.session_state.messages = []
    gc.collect()

def create_dynamic_model(fields):
    """Create a dynamic Pydantic model from schema fields."""
    field_annotations = {}
    for field in fields:
        if field["name"]:
            # Convert string type names to actual types
            type_mapping = {
                "str": str,
                "bool": bool,
                "int": int,
                "float": float
            }
            field_annotations[field["name"]] = type_mapping[field["type"]]
    
    # Dynamically create the model class
    return type(
        "ExtractSchema",
        (BaseModel,),
        {
            "__annotations__": field_annotations
        }
    )

def create_schema_from_fields(fields):
    """Create schema using Pydantic model."""
    if not any(field["name"] for field in fields):
        return None
    
    model_class = create_dynamic_model(fields)
    return model_class.model_json_schema()

def convert_to_table(data):
    """Convert a list of dictionaries to a markdown table."""
    if not data:
        return ""
    
    # Convert only the data field to a pandas DataFrame
    df = pd.DataFrame(data)
    
    # Convert DataFrame to markdown table
    return df.to_markdown(index=False)

def stream_text(text: str, delay: float = 0.001) -> None:
    """Stream text with a typing effect."""
    placeholder = st.empty()
    displayed_text = ""
    
    for char in text:
        displayed_text += char
        placeholder.markdown(displayed_text)
        time.sleep(delay)
    
    return placeholder

# Main app layout
st.markdown("""
    # Convert ANY website into an API using <img src="data:image/png;base64,{}" width="250" style="vertical-align: -25px;">
""".format(base64.b64encode(open("assets/firecrawl.png", "rb").read()).decode()), unsafe_allow_html=True)



# Sidebar
with st.sidebar:
    st.header("Configuration")
    
    # Website URL input
    website_url = st.text_input("Enter Website URL", placeholder="https://example.com")
    
    st.divider()
    
    # Schema Builder
    st.subheader("Schema Builder (Optional)")
    
    for i, field in enumerate(st.session_state.schema_fields):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            field["name"] = st.text_input(
                "Field Name",
                value=field["name"],
                key=f"name_{i}",
                placeholder="e.g., company_mission"
            )
        
        with col2:
            field["type"] = st.selectbox(
                "Type",
                options=["str", "bool", "int", "float"],
                key=f"type_{i}",
                index=0 if field["type"] == "str" else ["str", "bool", "int", "float"].index(field["type"])
            )

    if len(st.session_state.schema_fields) < 5:  # Limit to 5 fields
        if st.button("Add Field ➕"):
            st.session_state.schema_fields.append({"name": "", "type": "str"})

# Chat interface
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask about the website..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        if not website_url:
            st.error("Please enter a website URL first!")
        else:
            try:
                with st.spinner("Extracting data from website..."):
                    app = load_app()
                    schema = create_schema_from_fields(st.session_state.schema_fields)
                    print(schema)
                    extract_params = {
                        'prompt': prompt
                    }
                    if schema:
                        extract_params['schema'] = schema
                        
                    data = app.extract(
                        [website_url],
                        extract_params
                    )
                    print(data)
                    # check if data['data'] is a list, if yes, pass data['data'] to convert_to_table
                    if isinstance(data['data'], list):
                        table = convert_to_table(data['data'])
                    else:
                        # find the first key in data['data']
                        key = list(data['data'].keys())[0]
                        table = convert_to_table(data['data'][key])
                    placeholder = stream_text(table)
                    st.session_state.messages.append({"role": "assistant", "content": table})
                    # st.markdown(table)
            
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

# Footer
st.markdown("---")
st.markdown("Built with Firecrawl and Streamlit")