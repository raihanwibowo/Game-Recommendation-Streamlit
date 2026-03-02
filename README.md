# 🎮 Game Recommendation AI

AI-powered game recommendation chatbot using local LLMs. Built with Ollama, FastAPI, Streamlit, and PostgreSQL.

## ✨ Features

- 🤖 **AI Chat Interface** - Natural conversation for game recommendations
- 📚 **Gaming Knowledge Base** - Curated game database (JSON files)
- 🧠 **Persistent Memory** - Learns from all conversations across sessions
- 🗄️ **PostgreSQL Database** - Stores chat history and builds knowledge
- 🔌 **REST API** - FastAPI backend with clean separation
- 🌍 **Multilingual** - English and Bahasa Indonesia support
- 🎯 **Gaming-Focused** - Only answers game-related questions
- 📊 **Performance Metrics** - Real-time response time tracking

## 🏗️ Architecture

```
┌─────────────────┐      HTTP API      ┌──────────────────┐      ┌─────────────┐
│  Streamlit UI   │ ──────────────────> │  FastAPI Backend │ ───> │   Ollama    │
│   (Frontend)    │                     │   (API Server)   │      │    (LLM)    │
└─────────────────┘                     └──────────────────┘      └─────────────┘
        │                                        │
        v                                        v
┌─────────────────┐                     ┌──────────────────┐
│   PostgreSQL    │                     │  Knowledge Base  │
│  (Chat History) │                     │  (JSON Files)    │
└─────────────────┘                     └──────────────────┘
```

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL
- Ollama

## 🚀 Quick Start

### 1. Install Ollama

**macOS:** `brew install ollama`  
**Linux:** `curl -fsSL https://ollama.com/install.sh | sh`  
**Windows:** Download from [ollama.ai](https://ollama.ai)

Start Ollama: `ollama serve`

### 2. Download AI Model

```bash
ollama pull llama3.2:3b    # Recommended: Fast and efficient
```

### 3. Install PostgreSQL

**macOS:** `brew install postgresql@14 && brew services start postgresql@14`  
**Linux:** `sudo apt install postgresql && sudo systemctl start postgresql`  
**Windows:** Download from [postgresql.org](https://postgresql.org)

Create database: `createdb game_recommendation`

### 4. Setup Project

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Setup database
python src/setup_database.py
```

### 5. Configure `.env`

```env
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
DATABASE_URL=postgresql://localhost/game_recommendation
API_URL=http://localhost:8000
```

### 6. Run

**Terminal 1 - Backend:**
```bash
cd src/backend
python main.py
```

**Terminal 2 - Frontend:**
```bash
streamlit run src/app.py
```

**Access:**
- Frontend: http://localhost:8501
- API Docs: http://localhost:8000/docs

## 📁 Project Structure

```
src/
├── backend/                    # FastAPI Backend
│   ├── main.py                # API server entry point
│   ├── config.py              # Configuration management
│   ├── models.py              # Pydantic models
│   ├── routes/                # API endpoints
│   │   ├── chat.py           # Chat endpoint
│   │   └── health.py         # Health checks
│   └── services/              # Business logic
│       ├── chat_service.py   # Conversation management
│       ├── knowledge_base.py # JSON knowledge base
│       ├── ollama_service.py # Ollama integration
│       └── database_service.py # PostgreSQL access
│
├── packages/                   # Shared Utilities
│   ├── api_client.py          # Backend API client
│   ├── database.py            # PostgreSQL handler
│   └── utils.py               # Helper functions
│
├── ui/                         # UI Components
│   └── ui.py                  # Streamlit interface
│
├── data/knowledge/             # Knowledge Base
│   ├── games_database.json    # Game information
│   ├── genres.json            # Genre definitions
│   └── platforms.json         # Platform data
│
├── app.py                      # Frontend entry point
└── setup_database.py           # Database initialization
```

## 🔌 API Endpoints

### `GET /`
Service information

### `GET /health`
Health check - verifies Ollama connection

### `GET /models`
List available Ollama models

### `POST /chat`
Generate AI response

**Request:**
```json
{
  "prompt": "Recommend RPG games",
  "messages": [{"role": "user", "content": "Hello"}],
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

Full API docs: http://localhost:8000/docs

## 🗄️ Database Schema

**sessions** - User chat sessions
```sql
CREATE TABLE sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**messages** - Chat history
```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);
```

## 🎯 Recommended Models

| Model | Size | Speed | Quality | Use Case |
|-------|------|-------|---------|----------|
| **llama3.2:3b** | 2GB | ⚡⚡⚡ | ⭐⭐ | **Recommended** - Fast and efficient |
| **mistral:7b** | 4GB | ⚡⚡ | ⭐⭐⭐ | Better quality responses |
| **gemma2:9b** | 6GB | ⚡ | ⭐⭐⭐⭐ | High-quality, detailed answers |

## 🛠️ Configuration

### Environment Variables (`.env`)

```env
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
DATABASE_URL=postgresql://localhost/game_recommendation
API_URL=http://localhost:8000
```

### Model Parameters

Edit `src/backend/services/ollama_service.py`:
```python
"options": {
    "temperature": 0.7,      # Creativity (0.0-1.0)
    "num_predict": 800,      # Max response tokens
    "num_ctx": 8192          # Context window size
}
```

## 🐛 Troubleshooting

**Ollama not connected:**
```bash
ollama serve
ollama list  # Verify model is installed
```

**Database error:**
```bash
pg_isready  # Check PostgreSQL is running
psql -d game_recommendation  # Test connection
```

**API not responding:**
```bash
curl http://localhost:8000/health
cd src/backend && python main.py  # Restart backend
```

**Port in use:**
```bash
lsof -ti:8000 | xargs kill -9  # Kill backend
lsof -ti:8501 | xargs kill -9  # Kill frontend
```

## 💡 How It Works

1. **User sends message** → Streamlit UI
2. **UI calls API** → FastAPI backend
3. **Backend builds context:**
   - Loads gaming knowledge base (JSON files)
   - Extracts learned knowledge from PostgreSQL
   - Adds conversation history
4. **Sends to Ollama** → Local LLM generates response
5. **Returns to user** → Displays in chat interface
6. **Saves to database** → PostgreSQL stores for future learning

## 📝 License

MIT License

## 🙏 Built With

- [Ollama](https://ollama.ai) - Local LLM runtime
- [FastAPI](https://fastapi.tiangolo.com) - API framework
- [Streamlit](https://streamlit.io) - UI framework
- [PostgreSQL](https://postgresql.org) - Database

---

**Built with ❤️ for gamers**
