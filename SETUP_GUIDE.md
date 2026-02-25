# Quick Setup Guide

## Fix "Model not found" Error

If you see "Error: Ollama returned status 404", it means the model isn't installed.

### Check what models you have:
```bash
ollama list
```

### Install a model:

**Option 1: Mistral (Recommended - Fast & Good)**
```bash
ollama pull mistral
```

**Option 2: Llama 2**
```bash
ollama pull llama2
```

**Option 3: Phi (Fastest)**
```bash
ollama pull phi
```

### Update your .env file:

Create a `.env` file with:
```
OLLAMA_MODEL=mistral
```

**Important:** Use just the model name without the version tag!
- ✅ Correct: `mistral`
- ❌ Wrong: `mistral:7b` or `mistral:7B`

### Start Ollama:
```bash
ollama serve
```

### Run the app:
```bash
streamlit run app.py
```

## Common Issues

**"Cannot connect to Ollama"**
- Make sure Ollama is running: `ollama serve`

**"Request timed out"**
- Use a faster model like `phi` or `mistral`
- Or reduce `num_predict` in app.py (line ~45)

**Model takes too long**
- Try: `ollama pull phi` (smallest/fastest)
- Update .env: `OLLAMA_MODEL=phi`
