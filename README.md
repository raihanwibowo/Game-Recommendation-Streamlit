# 🎮 Game Recommendation AI

Get personalized game recommendations using AI that runs locally on your computer. No API keys, completely free and private.

## Quick Start

1. **Install Ollama** from [ollama.ai](https://ollama.ai)

2. **Download a model**:
```bash
ollama pull llama2
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Run the app**:
```bash
streamlit run app.py
```

## What It Does

- Get game recommendations based on games you've played
- Find similar games by genre or gameplay style
- Discover gaming websites and YouTube channels
- Save your preferences and recommendation history

## Configuration (Optional)

Create a `.env` file to customize:
```bash
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

Available models: `llama2`, `llama3`, `mistral`, `phi`

## Troubleshooting

**Can't connect to Ollama?**
```bash
ollama serve
```

**Model not found?**
```bash
ollama list
ollama pull llama2
```

## Requirements

- Python 3.8+
- Ollama running locally
