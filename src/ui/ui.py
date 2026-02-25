"""UI components and layout"""
import streamlit as st
import os
from packages.model import get_available_models


def setup_page_config():
    """Configure the Streamlit page"""
    st.set_page_config(
        page_title="Game Recommendation AI", 
        page_icon="🎮", 
        layout="wide"
    )


def render_title():
    """Render the main title"""
    st.title("🎮 Game Recommendation AI")
    st.markdown("Ask me anything about games!")


def render_sidebar(messages):
    """Render the sidebar with settings and info"""
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Model info
        ollama_model = os.getenv('OLLAMA_MODEL', 'llama3.2:3b')
        available_models = get_available_models()
        
        if available_models:
            st.success(f"✅ Connected to Ollama")
            st.caption(f"Model: **{ollama_model}**")
            if ollama_model not in available_models:
                st.warning(f"⚠️ Run: `ollama pull {ollama_model.split(':')[0]}`")
        else:
            st.caption(f"Model: {ollama_model}")
        
        st.divider()
        
        # Internet search toggle
        use_internet = st.checkbox(
            "🌐 Enable internet search", 
            value=True, 
            help="Search the web for current game information"
        )
        
        st.divider()
        
        # Clear chat button
        clear_chat = st.button("🗑️ Clear Display", use_container_width=True)
        
        # Show knowledge base size
        if messages:
            st.caption(f"📚 Total Knowledge: {len(messages)} messages")
            st.caption("💡 Clearing only clears display")
            st.caption("Knowledge is always saved!")
        
        st.divider()
        st.caption("💡 Ask me about games!")
        st.caption("Examples:")
        st.caption("• Recommend games like Elden Ring")
        st.caption("• Best RPGs of 2024")
        st.caption("• Games with great stories")
        st.caption("• Horror games for beginners")
        
        return use_internet, clear_chat


def render_chat_messages(messages):
    """Render all chat messages"""
    for message in messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def get_chat_input():
    """Get user input from chat"""
    return st.chat_input("Ask me about games...")
