"""
UI Utility Functions for RAG-SQL Assistant

This module provides utility functions for UI components.
"""

import streamlit as st
import time
import random
from typing import List

def stream_text_with_cursor(text: str):
    """
    Stream text with a red cursor effect while preserving markdown formatting.
    
    Args:
        text: The text to stream
    """
    # Create a placeholder for the streaming text
    placeholder = st.empty()
    
    # Stream the text character by character or in chunks to preserve markdown
    displayed_text = ""
    
    # Define the chunk size for streaming (adjust for better performance)
    chunk_size = 3  # Stream a few characters at a time
    
    for i in range(0, len(text), chunk_size):
        # Get the next chunk of text
        chunk = text[i:i+chunk_size]
        
        # Add the chunk to the displayed text
        displayed_text += chunk
        
        # Display text with red cursor
        placeholder.markdown(f"{displayed_text}<span style='color:red; font-size:1.25em; font-weight:bold;'>|</span>", unsafe_allow_html=True)
        
        # Small random delay between chunks (0.01 to 0.05 seconds)
        time.sleep(random.uniform(0.01, 0.05))
    
    # Final text without cursor
    placeholder.markdown(displayed_text)
    
    return displayed_text