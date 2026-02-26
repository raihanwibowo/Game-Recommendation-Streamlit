"""Main application entry point"""
import streamlit as st
from dotenv import load_dotenv
import uuid

# Load environment variables from .env file
load_dotenv()

from ui.ui import (
    setup_page_config, 
    render_title, 
    render_sidebar, 
    render_chat_messages, 
    get_chat_input
)
from packages.model import get_llm_response
from packages.database import get_database

# Initialize database
db = get_database()

# Page config
setup_page_config()

# Initialize session state
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    db.create_session(st.session_state.session_id)

if 'messages' not in st.session_state:
    # Load messages from database
    st.session_state.messages = db.get_messages(st.session_state.session_id)

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
    
    # Save to database
    db.save_message(st.session_state.session_id, "user", prompt)
    
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
        
        # Save to database
        db.save_message(st.session_state.session_id, "assistant", response)

