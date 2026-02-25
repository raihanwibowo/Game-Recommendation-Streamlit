"""Model interaction and response generation"""
import requests
import json
import os
import streamlit as st
from datetime import datetime
from packages.utils import search_internet


def get_available_models():
    """Get list of available Ollama models"""
    try:
        ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            return [model['name'] for model in models]
        return []
    except:
        return []


def build_conversation_context(messages):
    """Build conversation history for context"""
    context = ""
    # Include last 10 messages for context (to keep prompt size manageable)
    recent_messages = messages[-10:] if len(messages) > 10 else messages
    
    if recent_messages:
        context = "\n\n--- CONVERSATION HISTORY (Your Knowledge Base) ---\n"
        for msg in recent_messages:
            role = msg["role"].capitalize()
            context += f"{role}: {msg['content']}\n\n"
        context += "--- END CONVERSATION HISTORY ---\n\n"
    
    return context


def get_llm_response(prompt, messages, use_search=False):
    """Get response from Ollama with streaming support and optional internet search"""
    try:
        ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
        model = os.getenv('OLLAMA_MODEL', 'llama3.2:3b')
        
        # Build conversation context from previous messages
        conversation_context = build_conversation_context(messages)
        
        # Add internet search context if enabled
        search_context = ""
        if use_search:
            with st.spinner("🔍 Searching the internet..."):
                search_results = search_internet(prompt)
                if search_results and "Search error" not in search_results:
                    search_context = f"\n\n--- INTERNET SEARCH RESULTS (Current as of {datetime.now().strftime('%Y-%m-%d')}) ---\n{search_results}\n--- END SEARCH RESULTS ---\n\nUse the above search results to provide accurate and up-to-date information.\n\n"
        
        # System message
        system_message = """You are a gaming expert AI assistant specializing ONLY in video game recommendations and gaming topics.

STRICT RULES:
1. ONLY answer questions about video games, gaming platforms, game recommendations, gaming hardware, and gaming culture
2. If asked about non-gaming topics (politics, health, finance, general knowledge, etc.), politely decline and redirect to gaming
3. Examples of acceptable topics: game recommendations, game reviews, gaming tips, platform comparisons, gaming news
4. Examples of unacceptable topics: cooking, math problems, history, science, personal advice (unless gaming-related)

LANGUAGE RULES:
- ALWAYS respond in the SAME LANGUAGE as the user's question
- If user asks in English, respond in English
- If user asks in Bahasa Indonesia, respond in Bahasa Indonesia
- Match the user's language naturally and fluently

RESPONSE FORMAT:
- If the question is about games: Answer enthusiastically with detailed gaming knowledge IN THE USER'S LANGUAGE
- If the question is NOT about games in English: "I'm a gaming specialist AI! I can only help with video game recommendations and gaming-related questions. Ask me about games, gaming platforms, or what to play next! 🎮"
- If the question is NOT about games in Bahasa Indonesia: "Saya adalah AI spesialis gaming! Saya hanya bisa membantu dengan rekomendasi video game dan pertanyaan seputar gaming. Tanyakan tentang game, platform gaming, atau game apa yang harus dimainkan selanjutnya! 🎮"

Use your conversation history as your knowledge base - remember what you've already discussed about games.
If search results are provided, use them to give accurate, current information about games.
Be conversational, enthusiastic, and knowledgeable about gaming."""
        
        # Combine everything with conversation context
        full_prompt = f"{system_message}{conversation_context}{search_context}\n\nUser: {prompt}\n\nAssistant:"
        
        response = requests.post(
            f"{ollama_url}/api/generate",
            json={
                "model": model,
                "prompt": full_prompt,
                "stream": True,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 800
                }
            },
            stream=True,
            timeout=180
        )
        
        if response.status_code == 200:
            full_response = ""
            message_placeholder = st.empty()
            
            for line in response.iter_lines():
                if line:
                    json_response = json.loads(line)
                    if 'response' in json_response:
                        full_response += json_response['response']
                        message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            return full_response
            
        elif response.status_code == 404:
            available = get_available_models()
            if available:
                return f"❌ Model '{model}' not found. Available: {', '.join(available)}. Run `ollama pull {model.split(':')[0]}`"
            else:
                return f"❌ Model '{model}' not found. Run `ollama pull {model.split(':')[0]}`"
        else:
            return f"❌ Ollama returned status {response.status_code}"
            
    except requests.exceptions.ConnectionError:
        return "❌ Cannot connect to Ollama. Make sure it's running with `ollama serve`"
    except requests.exceptions.Timeout:
        return "❌ Request timed out. Try a faster model or reduce num_predict."
    except Exception as e:
        return f"❌ Error: {str(e)}"
