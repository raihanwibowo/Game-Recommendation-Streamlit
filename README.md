# 🎮 Game Recommendation AI

A Streamlit app that uses Ollama (local LLM) to provide personalized game recommendations based on your gaming preferences.

## Features

1. **Game Recommendations** - Enter a game you've played and get similar recommendations
2. **Genre-Based Recommendations** - Get suggestions based on your favorite genres
3. **Personalized Suggestions** - Tell the AI what you like and get tailored recommendations
4. **Gaming Resources** - Find websites and YouTube channels for specific games
5. **Preference Learning** - The app learns your preferences over time

## Prerequisites

1. **Install Ollama**: Download from [ollama.ai](https://ollama.ai)

2. **Pull a model** (choose one):
```bash
# Recommended for gaming recommendations
ollama pull llama2
# or
ollama pull mistral
# or
ollama pull llama3
```

3. **Start Ollama**:
```bash
ollama serve
```

## Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. (Optional) Create a `.env` file to customize settings:
```bash
cp .env.example .env
# Edit .env to change model or URL if needed
```

3. Run the app:
```bash
streamlit run app.py
```

## Configuration

You can configure the app via `.env` file:

- `OLLAMA_URL` - Ollama server URL (default: `http://localhost:11434`)
- `OLLAMA_MODEL` - Model to use (default: `llama2`)

Available models you can use:
- `llama2` - Good balance of speed and quality
- `llama3` - Better quality, slower
- `mistral` - Fast and efficient
- `codellama` - Optimized for technical content
- `phi` - Lightweight and fast

## Usage

### Tab 1: Game Recommendations
- Enter a game you've played
- Choose recommendation type (similar games, same genre, or based on preferences)
- Get instant recommendations with descriptions

### Tab 2: Gaming Resources
- Enter a game name
- Get recommended websites (wikis, forums, guides)
- Get YouTube channel recommendations for gameplay and tutorials

### Tab 3: Genre Deep Dive
- Describe your gaming preferences in detail
- Get highly personalized recommendations based on what you enjoy

### Sidebar
- Select your favorite genres
- Add notes about your playstyle
- View and clear recommendation history

## Troubleshooting

**"Cannot connect to Ollama" error:**
- Make sure Ollama is running: `ollama serve`
- Check if the model is installed: `ollama list`
- Verify Ollama is accessible: `curl http://localhost:11434/api/tags`

**Slow responses:**
- Try a smaller/faster model like `mistral` or `phi`
- Reduce the `num_predict` parameter in the code

## Requirements

- Python 3.8+
- Ollama installed and running
- At least one Ollama model pulled

## Benefits of Using Ollama

- ✅ Completely free and private
- ✅ No API keys needed
- ✅ Works offline
- ✅ Fast responses with local processing
- ✅ Multiple model options
