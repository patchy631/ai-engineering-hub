"""
UI Module for RAG-SQL Assistant

This package provides all UI components for the RAG-SQL Assistant application.
"""

from src.ui.chat import (
    initialize_chat_state,
    reset_chat,
    display_chat_history,
    display_message,
    add_user_message,
    add_assistant_message,
    chat_input_area
)

from src.ui.main import (
    setup_page_config,
    render_sidebar,
    render_header,
    render_main_ui
)

from src.ui.explainer import (
    render_explainer_section,
    render_about_section
)

from src.ui.utils import (
    stream_text_with_cursor
)

__all__ = [
    # Chat UI
    "initialize_chat_state",
    "reset_chat",
    "display_chat_history",
    "display_message",
    "add_user_message",
    "add_assistant_message",
    "chat_input_area",
    
    # Main UI
    "setup_page_config",
    "render_sidebar",
    "render_header",
    "render_main_ui",
    
    # Explainer UI
    "render_explainer_section",
    "render_about_section",
    
    # UI Utilities
    "stream_text_with_cursor"
]
