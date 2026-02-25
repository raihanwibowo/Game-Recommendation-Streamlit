"""Main application entry point"""
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from ui import (
    setup_page_config, 
    render_title, 
    render_sidebar, 
    render_chat_messages, 
    get_chat_input
)
from model import get_llm_response
from utils import save_chat_history, load_chat_history, delete_chat_history


# Page config
setup_page_config()

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = load_chat_history()

if 'display_messages' not in st.session_state:
    st.session_state.display_messages = []

# Render UI
render_title()
use_internet, clear_chat = render_sidebar(st.session_state.display_messages)

# Handle clear chat (only clears display, not saved history)
if clear_chat:
    st.session_state.display_messages = []
    st.rerun()

# Display chat messages (only display messages)
render_chat_messages(st.session_state.display_messages)

# Chat input
if prompt := get_chat_input():
    # Add user message to both display and persistent storage
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.display_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get assistant response (uses full message history for context)
    with st.chat_message("assistant"):
        response = get_llm_response(
            prompt, 
            st.session_state.messages,  # Use full history for context
            use_search=use_internet
        )
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.display_messages.append({"role": "assistant", "content": response})
    
    # Always save chat history for persistent knowledge
    save_chat_history(st.session_state.messages)
