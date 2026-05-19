# Antigravity Second Brain 🧠

A comprehensive, local-first agentic "Second Brain" system designed to capture, classify, and instantly retrieve your knowledge. It integrates a WhatsApp conversational agent with a premium, high-tech Web Dashboard built on FastAPI.

## Key Features

### 1. WhatsApp Agent (LangGraph)
- **Natural Language Processing:** Send unstructured thoughts, ideas, or to-dos directly to your WhatsApp bot.
- **Agentic Routing:** Uses a `LangGraph` state graph to dynamically classify incoming messages into Action Items, Ideas, or Knowledge Notes.
- **Live Internet Search:** The bot automatically cross-references your queries using DuckDuckGo to provide real-time information.

### 2. Document Intelligence & RAG
- **PDF Uploads:** Upload massive documents (like Interview Guides or Textbooks) directly to the Web Dashboard.
- **Vector Database (ChromaDB):** Documents are automatically sliced into chunks and converted into mathematical vectors stored locally.
- **Retrieval-Augmented Generation (RAG):** When you ask the chatbot a question, it searches your local `ChromaDB` Wiki first, injecting your personal notes into its prompt to provide highly accurate, customized answers.

### 3. Premium Web Dashboard
- **Wikipedia-Style Viewing:** A dedicated split-screen UI that allows you to read beautiful AI-generated markdown summaries right alongside the original PDF document.
- **High-Tech Aesthetics:** Built with custom glassmorphism, neon glows, cyber-scrollbars, and smooth CSS fade-in animations for a state-of-the-art UI experience.
- **Local-First:** All data (SQLite DB, ChromaDB vectors, and PDF uploads) is stored securely on your local machine (`/storage`).

---

## Prerequisites

- Python 3.11+
- Ngrok (for local webhook testing with WhatsApp)
- Meta WhatsApp Cloud API credentials
- OpenAI API Key

## Installation

1. **Clone or Enter the Directory:**
   Navigate into the `second-brain-agent` project directory.

2. **Activate the Virtual Environment:**
   ```bash
   # Windows
   .venv\Scripts\activate
   
   # Mac/Linux
   source .venv/bin/activate
   ```

3. **Install Dependencies:**
   Install core requirements including FastAPI, LangGraph, ChromaDB, and DuckDuckGo-Search.
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables:**
   Rename `.env.example` to `.env` and fill in your API keys (OpenAI, WhatsApp tokens).

## Running the Application Locally

1. **Start the FastAPI Server:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   *Access the Web Dashboard at `http://localhost:8000`*

2. **Expose Localhost for WhatsApp Webhook:**
   Run ngrok in a separate terminal to expose your local server to Meta's WhatsApp servers:
   ```bash
   ngrok http 8000
   ```
   Copy the `https://...ngrok-free.app` URL and configure your Meta WhatsApp Webhook to point to `https://<ngrok-url>/webhook/whatsapp`.

---

## Architecture

- **`app/main.py`**: The FastAPI application handling the Web Dashboard and static file serving.
- **`app/graph.py`**: The LangGraph state machine orchestrating the chatbot's decision making.
- **`app/routers/whatsapp_router.py`**: The webhook endpoint receiving messages from Meta.
- **`app/routers/upload_router.py`**: Handles PDF ingestion, AI summarization, and ChromaDB embedding.
- **`app/nodes/research.py`**: The intelligence node executing dual-searches against your local Wiki (`ChromaDB`) and the Live Web (`DuckDuckGo`).
- **`app/vector_db.py`**: Manages the persistent local ChromaDB instance.
- **`templates/` & `static/`**: HTML/CSS/JS for the premium Web Dashboard.
