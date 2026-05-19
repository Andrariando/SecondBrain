# Antigravity Second Brain 🧠

A comprehensive, local-first Multi-Agent "Second Brain" system designed to capture, classify, and instantly retrieve your knowledge. It integrates a WhatsApp conversational agent powered by an autonomous LangGraph agent team with a premium, high-tech Web Dashboard.

## 🚀 Tech Stack

- **Backend:** FastAPI, Python 3.11+
- **AI Orchestration:** LangGraph & LangChain (Multi-Agent ReAct Architecture)
- **Vector Database:** ChromaDB (Local RAG)
- **Relational Database:** SQLite (SQLAlchemy ORM)
- **Frontend:** Vanilla JS, HTML5, CSS3 (Glassmorphism, CSS Micro-animations)
- **Search & Scraping:** DuckDuckGo-Search, BeautifulSoup4
- **Messaging:** Meta WhatsApp Cloud API

---

## 🤖 The Multi-Agent Architecture

The core of the system is no longer a rigid state machine. It is a fully autonomous **Multi-Agent System (MAS)** where specialized AI agents collaborate to fulfill your complex WhatsApp requests:

1. **👔 The Supervisor:** The master router. It reads your incoming WhatsApp messages and delegates work to the specialized workers below. 
2. **📚 The Librarian:** The Wiki specialist. Equipped with a `search_wiki` tool to query your local ChromaDB for context from your uploaded PDFs.
3. **🌐 The Researcher:** The Internet crawler. Equipped with `search_web` and `scrape_website` tools to find breaking news via DuckDuckGo and autonomously read full web articles.
4. **📋 The Project Manager:** The Data Entry expert. Equipped with `save_action_item`, `save_idea`, `get_pending_tasks`, and `search_ideas` tools to seamlessly read and write directly to your SQLite database.
5. **📊 The Analyst:** The math and logic specialist. Equipped with an isolated `run_python` sandbox tool to write and execute python code for 100% mathematically flawless calculations and data analysis.

---

## 💻 Premium Web Dashboard

- **Split-Screen Wiki Viewing:** Read beautiful AI-generated markdown summaries right alongside the original embedded PDF document.
- **Dynamic Search & Filtering:** A high-tech search bar instantly filters your Knowledge Base and Action Items across titles and content.
- **Source Traceability:** Every memory card contains a source badge linking it back to the exact PDF it was generated from.
- **High-Tech Aesthetics:** Built with custom glassmorphism, neon glows, cyber-scrollbars, and smooth CSS fade-in animations for a state-of-the-art UI experience.
- **Local-First Privacy:** All data (SQLite DB, ChromaDB vectors, and PDF uploads) is stored securely on your local machine (`/storage`).

---

## ⚙️ Installation & Setup

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/Andrariando/SecondBrain.git
   cd SecondBrain/second-brain-agent
   ```

2. **Activate the Virtual Environment:**
   ```bash
   # Windows
   .venv\Scripts\activate
   
   # Mac/Linux
   source .venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables:**
   Rename `.env.example` to `.env` and fill in your API keys (OpenAI, WhatsApp tokens).

## 🏃 Running the Application

1. **Start the FastAPI Server:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   *Access the Web Dashboard at `http://localhost:8000`*

2. **Expose Localhost for WhatsApp Webhook:**
   Run ngrok in a separate terminal:
   ```bash
   ngrok http 8000
   ```
   Configure your Meta WhatsApp Webhook to point to `https://<ngrok-url>/whatsapp`.
