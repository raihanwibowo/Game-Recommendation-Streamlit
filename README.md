# 🎮 Game Recommendation AI

AI-powered game recommendation system with chat interface, internet search, and persistent knowledge base. Built with Ollama, FastAPI, Streamlit, and PostgreSQL.

## ✨ Features

- 🤖 **AI Chat Interface** - ChatGPT-style conversation for game recommendations
- 🌐 **Internet Search** - Real-time game information from the web
- 🧠 **Persistent Memory** - Learns from conversations and remembers preferences
- 🗄️ **PostgreSQL Database** - Scalable storage for chat history
- 🔌 **REST API** - FastAPI backend for flexible integration
- 🌍 **Multilingual** - Responds in English or Bahasa Indonesia
- 🎯 **Gaming-Focused** - Only answers game-related questions
- 📊 **Performance Metrics** - Real-time response time and token tracking

## 🏗️ Architecture

```
┌─────────────────┐      HTTP API      ┌──────────────────┐      ┌─────────────┐
│  Streamlit UI   │ ──────────────────> │  FastAPI Backend │ ───> │   Ollama    │
│   (Frontend)    │                     │   (API Server)   │      │   (Model)   │
└─────────────────┘                     └──────────────────┘      └─────────────┘
        │                                        │
        v                                        v
┌─────────────────┐                     ┌──────────────────┐
│   PostgreSQL    │                     │  DuckDuckGo API  │
│  (Chat History) │                     │ (Internet Search)│
└─────────────────┘                     └──────────────────┘
```

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL 14+
- Ollama

## 🚀 Quick Start

### 1. Install Ollama

**macOS:**
```bash
brew install ollama
ollama serve
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama serve
```

**Windows:** Download from [ollama.ai](https://ollama.ai)

### 2. Download AI Model

```bash
# Recommended: Mistral 7B (good balance of speed and quality)
ollama pull mistral:7b

# Or other options:
ollama pull llama3.2:3b    # Faster, smaller
ollama pull gemma2:9b      # Better quality
ollama pull qwen2.5:7b     # Multilingual
```

### 3. Install PostgreSQL

**macOS:**
```bash
brew install postgresql@14
brew services start postgresql@14
createdb game_recommendation
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo -u postgres createdb game_recommendation
```

**Windows:** Download from [postgresql.org](https://www.postgresql.org/download/windows/)

### 4. Setup Project

```bash
# Clone repository
git clone <your-repo-url>
cd recommendation-game-service

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Setup database
python src/setup_database.py
```

### 5. Configure Environment

Edit `.env` file:

```env
# Ollama Configuration
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=mistral:7b

# PostgreSQL Database
DATABASE_URL=postgresql://username:password@localhost:5432/game_recommendation

# Backend API URL
API_URL=http://localhost:8000
```

### 6. Run the Application

**Terminal 1 - Start Backend API:**
```bash
cd src/backend
python main.py
```

**Terminal 2 - Start Frontend:**
```bash
streamlit run src/app.py
```

**Access:**
- Frontend: http://localhost:8501
- API Docs: http://localhost:8000/docs
- API Health: http://localhost:8000/health

## 📁 Project Structure

```
recommendation-game-service/
├── src/
│   ├── backend/              # FastAPI backend
│   │   ├── main.py          # API server
│   │   ├── requirements.txt # Backend dependencies
│   │   └── .env.example     # Backend config template
│   │
│   ├── packages/            # Shared modules
│   │   ├── api_client.py   # API client
│   │   ├── database.py     # PostgreSQL handler
│   │   ├── model.py        # Model logic (legacy)
│   │   └── utils.py        # Utilities
│   │
│   ├── ui/                  # UI components
│   │   └── ui.py           # Streamlit UI
│   │
│   ├── data/                # Data storage
│   │   └── chat_history.json (legacy)
│   │
│   ├── app.py              # Streamlit frontend entry
│   └── setup_database.py   # Database setup script
│
├── requirements.txt         # Frontend dependencies
├── .env                     # Environment config
└── README.md               # This file
```

## 🔌 API Documentation

### Endpoints

#### `GET /`
Service information
```json
{
  "service": "Game Recommendation API",
  "status": "running",
  "version": "1.0.0"
}
```

#### `GET /health`
Health check
```json
{
  "status": "healthy",
  "ollama": "connected",
  "timestamp": "2025-02-26T10:30:00"
}
```

#### `GET /models`
Available Ollama models
```json
{
  "name": "mistral:7b",
  "available": true,
  "models": ["mistral:7b", "llama3.2:3b"]
}
```

#### `POST /chat`
Generate chat response

**Request:**
```json
{
  "prompt": "Recommend RPG games",
  "messages": [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi!"}
  ],
  "use_search": false,
  "temperature": 0.7,
  "max_tokens": 800
}
```

**Response:**
```json
{
  "response": "Here are some great RPG games...",
  "inference_time": 2.5,
  "tokens_per_second": 45.2,
  "prompt_tokens": 450,
  "response_tokens": 113
}
```

## 🗄️ Database Schema

### Tables

**sessions**
```sql
CREATE TABLE sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**messages**
```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
);
```

## 🎯 Recommended Models

| Model | Size | Speed | Quality | Use Case |
|-------|------|-------|---------|----------|
| **llama3.2:3b** | 2GB | ⚡⚡⚡ | ⭐⭐ | Fast responses, basic recommendations |
| **mistral:7b** | 4GB | ⚡⚡ | ⭐⭐⭐ | **Recommended** - Best balance |
| **gemma2:9b** | 6GB | ⚡ | ⭐⭐⭐⭐ | Detailed, high-quality responses |
| **qwen2.5:7b** | 4GB | ⚡⚡ | ⭐⭐⭐ | Multilingual support |
| **llama3.3:70b** | 40GB | ⚡ | ⭐⭐⭐⭐⭐ | Best quality (requires powerful GPU) |

## 🛠️ Configuration Options

### Environment Variables

```env
# Ollama
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=mistral:7b

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/game_recommendation

# API
API_URL=http://localhost:8000
```

### Model Parameters

Edit `src/backend/main.py`:
```python
"options": {
    "temperature": 0.7,      # Creativity (0.0-1.0)
    "num_predict": 800       # Max response tokens
}
```

## 🐛 Troubleshooting

### Ollama Connection Error
```bash
# Check if Ollama is running
ollama list

# Start Ollama
ollama serve
```

### Model Not Found
```bash
# List installed models
ollama list

# Pull missing model
ollama pull mistral:7b
```

### Database Connection Error
```bash
# Check PostgreSQL status
pg_isready

# Start PostgreSQL
brew services start postgresql@14  # macOS
sudo systemctl start postgresql    # Linux

# Test connection
psql -d game_recommendation
```

### API Connection Error
```bash
# Check if backend is running
curl http://localhost:8000/health

# Restart backend
cd src/backend
python main.py
```

### Port Already in Use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 8501
lsof -ti:8501 | xargs kill -9
```

## 📊 Performance Tips

1. **Use appropriate model size** for your hardware
2. **Enable internet search** only when needed (adds latency)
3. **Adjust temperature** (lower = more focused, higher = more creative)
4. **Reduce max_tokens** for faster responses
5. **Use GPU** if available (Ollama auto-detects)

## 🚀 Production Deployment

### Backend (FastAPI)
```bash
# Using Uvicorn
uvicorn src.backend.main:app --host 0.0.0.0 --port 8000 --workers 4

# Using Gunicorn
gunicorn src.backend.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend (Streamlit)
```bash
streamlit run src/app.py --server.port 8501 --server.address 0.0.0.0
```

### Docker (Coming Soon)
```bash
docker-compose up -d
```

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

MIT License - feel free to use for personal or commercial projects

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai) - Local LLM runtime
- [FastAPI](https://fastapi.tiangolo.com) - Modern API framework
- [Streamlit](https://streamlit.io) - Rapid UI development
- [PostgreSQL](https://www.postgresql.org) - Reliable database
- [DuckDuckGo](https://duckduckgo.com) - Privacy-focused search

## 📧 Support

For issues and questions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review troubleshooting section above

---

**Built with ❤️ for gamers by gamers**
