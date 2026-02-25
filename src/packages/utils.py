"""Utility functions for search and file operations"""
import json
import os
from ddgs import DDGS
from datetime import datetime


def search_internet(query, max_results=5):
    """Search the internet using DuckDuckGo"""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            if results:
                formatted_results = []
                for idx, result in enumerate(results, 1):
                    formatted_results.append(
                        f"{idx}. {result['title']}\n"
                        f"   {result['body']}\n"
                        f"   Source: {result['href']}"
                    )
                return "\n\n".join(formatted_results)
            return "No search results found."
    except Exception as e:
        return f"Search error: {str(e)}"


def save_chat_history(messages):
    """Save chat history to file for persistent knowledge"""
    try:
        # Create data folder if it doesn't exist
        os.makedirs('data', exist_ok=True)
        with open('data/chat_history.json', 'w') as f:
            json.dump(messages, f)
    except:
        pass


def load_chat_history():
    """Load chat history from file"""
    if os.path.exists('data/chat_history.json'):
        try:
            with open('data/chat_history.json', 'r') as f:
                return json.load(f)
        except:
            pass
    return []


def delete_chat_history():
    """Delete chat history file"""
    if os.path.exists('data/chat_history.json'):
        os.remove('data/chat_history.json')
