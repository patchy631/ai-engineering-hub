"""
Explainer UI Component for RAG-SQL Assistant

This module provides the Streamlit UI components for explaining the RAG-SQL router,
including diagrams, explanations, and examples of how the system works.
"""

import streamlit as st
import os
from pathlib import Path
import base64

# Get the assets directory path
ASSETS_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent.parent / "assets"

def is_valid_image(file_path):
    """Check if a file is a valid image."""
    try:
        # Try to read the file
        with open(file_path, 'rb') as f:
            # Check if it's a text placeholder (our echo command created text files)
            content = f.read(30)  # Read the first few bytes
            if content.startswith(b'Placeholder'):
                return False
            
            # If not a placeholder, assume it's a valid image for now
            # In a production app, you'd verify the image format here
            return True
    except Exception:
        return False

def render_explainer_section():
    """Render the explainer section with information about how the RAG-SQL Assistant works."""
    
    st.markdown("""
    ## How the RAG-SQL Assistant Works
    
    This application combines **Retrieval-Augmented Generation (RAG)** and **Text-to-SQL** 
    capabilities to provide answers to your questions in the most appropriate way.
    
    ### System Architecture
    
    The system uses a **Router** to determine whether to use RAG or SQL based on your query:
    """)
    
    # Display architecture diagram
    architecture_path = ASSETS_DIR / "architecture.png"
    if os.path.exists(architecture_path) and is_valid_image(architecture_path):
        st.image(str(architecture_path), caption="RAG-SQL Assistant Architecture")
    else:
        # Display text explanation instead
        st.markdown("""
        ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
        │   User      │     │   Router    │     │   Response  │
        │   Query     │────▶│   Agent     │────▶│  Generation │
        └─────────────┘     └─────────────┘     └─────────────┘
                                  │
                          ┌───────┴───────┐
                          │               │
                    ┌─────▼────┐    ┌─────▼────┐
                    │   SQL    │    │   RAG    │
                    │   Tool   │    │   Tool   │
                    └──────────┘    └──────────┘
        """)
        st.markdown("""
        *Architecture Diagram: User queries are analyzed by a router agent which selects either the SQL or RAG tool.*
        """)
    
    st.markdown("""
    ### When is SQL used?
    
    The system uses SQL for:
    - Questions about aggregations (counts, sums, averages)
    - Questions about sorting or ranking data
    - Questions that require filtering on specific criteria
    - Questions about relationships between different data entities
    
    ### When is RAG used?
    
    The system uses RAG for:
    - Questions about concepts, definitions, or explanations
    - Questions that require background knowledge
    - Questions about processes or methodologies
    - Questions that don't map directly to structured database queries
    
    ### Example Queries
    
    **SQL Examples:**
    - "What is the population of New York City?"
    - "List the top 5 most populous cities in California."
    - "What is the average population of cities in Texas?"
    
    **RAG Examples:**
    - "Tell me about the history of Chicago."
    - "What are the major landmarks in Boston?"
    - "Explain the climate patterns in Seattle."
    """)
    
    # Add an expander with technical details
    with st.expander("Technical Details", expanded=False):
        st.markdown("""
        ### Implementation Details
        
        The RAG-SQL Assistant is built using:
        
        - **LlamaIndex**: Provides the workflow engine, RAG capabilities, and tool routing
        - **SQLAlchemy**: Handles database connection and SQL query execution
        - **Streamlit**: Powers the user interface
        
        The workflow process:
        
        1. User submits a natural language query
        2. The router LLM analyzes the query to determine the appropriate tool
        3. For SQL queries, the system generates SQL, validates it, and executes it against the database
        4. For RAG queries, the system retrieves relevant documents and generates a response
        5. The response is formatted and presented to the user with appropriate context
        """)
        
        # Add a diagram of the workflow steps if available
        workflow_path = ASSETS_DIR / "workflow.png"
        if os.path.exists(workflow_path) and is_valid_image(workflow_path):
            st.image(str(workflow_path), caption="Workflow Process")
        else:
            # Display text explanation instead
            st.markdown("""
            ┌─────────────┐
            │   User      │
            │   Query     │
            └──────┬──────┘
                   │
                   ▼
            ┌─────────────┐
            │   Query     │
            │   Analysis  │
            └──────┬──────┘
                   │
                   ▼
            ┌─────────────┐
            │  Tool       │
            │  Selection  │
            └──────┬──────┘
                   │
             ┌─────┴─────┐
             │           │
             ▼           ▼
        ┌─────────┐ ┌─────────┐
        │   SQL   │ │   RAG   │
        │  Query  │ │ Retrieval│
        └────┬────┘ └────┬────┘
             │           │
             ▼           ▼
        ┌─────────┐ ┌─────────┐
        │  DB     │ │ Document│
        │ Results │ │ Context │
        └────┬────┘ └────┬────┘
             │           │
             └─────┬─────┘
                   │
                   ▼
            ┌─────────────┐
            │  Response   │
            │ Generation  │
            └──────┬──────┘
                   │
                   ▼
            ┌─────────────┐
            │    User     │
            │  Response   │
            └─────────────┘
            """)
            st.markdown("""
            *Workflow Diagram: The system analyzes the query, chooses a tool, retrieves information, and generates a response.*
            """)

def render_about_section():
    """Render the About section with information about the project."""
    
    st.markdown("""
    ### About This Project
    
    This RAG-SQL Assistant demonstrates how to create a hybrid query system that combines 
    the strengths of both retrieval-augmented generation and text-to-SQL capabilities.
    
    The project was created as a demonstration for the Daily Dose of Data Science publication.
    
    **Source Code**: [GitHub Repository](https://github.com/patchy631/ai-engineering-hub)
    """)
    
    # Display Daily Dose of Data Science banner if available
    banner_path = ASSETS_DIR / "ddods_banner.png"
    if os.path.exists(banner_path) and is_valid_image(banner_path):
        st.image(str(banner_path))
    else:
        # Just display text instead
        st.markdown("""
        ## Daily Dose of Data Science
        *Learn, grow, and stay updated with the latest in data science.*
        """)
        
    st.markdown("""
    ---
    
    ## 📬 Stay Updated with Daily Dose of Data Science!
    
    **Get a FREE Data Science eBook** 📖 with 150+ essential lessons in Data Science 
    when you subscribe to our newsletter! Stay in the loop with the latest tutorials, 
    insights, and exclusive resources. 
    
    [Subscribe now!](https://join.dailydoseofds.com)
    """)
