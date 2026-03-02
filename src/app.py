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
from packages.database import get_database
from packages.api_client import get_api_client
import streamlit as st

# Initialize database and API client
db = get_database()
api_client = get_api_client()

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
        # Show thinking indicator
        with st.spinner("🤔 Thinking..."):
            # Call API instead of direct Ollama
            result = api_client.chat(
                prompt=prompt,
                messages=st.session_state.messages,
                use_search=use_internet
            )
        
        if result.get('error'):
            response = f"❌ Error: {result.get('message')}"
            st.error(response)
        else:
            response = result.get('response')
            inference_time = result.get('inference_time', 0)
            tokens_per_second = result.get('tokens_per_second', 0)
            
            # Display response with timing
            timing_info = f"\n\n---\n*⏱️ Response time: {inference_time}s | Tokens/sec: {tokens_per_second}*"
            st.markdown(response + timing_info)
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.display_messages.append({"role": "assistant", "content": response})
        
        # Save to database
        db.save_message(st.session_state.session_id, "assistant", response)

