# Antigravity Second Brain 🧠

A comprehensive, local-first **Autonomous Multi-Agent Second Brain** powered by LangGraph. It captures, classifies, and retrieves your knowledge through a premium Web Dashboard and a WhatsApp conversational interface. Your personal AI team handles everything from web research and code execution to managing your Google Calendar and Gmail — all running autonomously on your machine.

## 🚀 Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | FastAPI, Python 3.11+ |
| **AI Orchestration** | LangGraph & LangChain (Multi-Agent ReAct) |
| **LLM** | OpenAI GPT-4o, Whisper-1 |
| **Vector Database** | ChromaDB (Local RAG) |
| **Relational Database** | SQLite + SQLAlchemy ORM |
| **Frontend** | Vanilla JS, HTML5, CSS3 (Glassmorphism, Animated Orbs, Outfit Font) |
| **Search & Scraping** | DuckDuckGo-Search, BeautifulSoup4 |
| **Messaging** | Meta WhatsApp Cloud API |
| **Multimodal** | OpenAI Vision (GPT-4o), OpenAI Audio (Whisper-1) |
| **Productivity** | Google Calendar API, Gmail API (Google Workspace) |

---

## 🤖 The Multi-Agent Architecture

The core of the system is a fully autonomous **Multi-Agent System (MAS)** where 6 specialized AI agents collaborate via LangGraph's ReAct pattern:

1. **👔 The Supervisor:** The master router. Reads every incoming WhatsApp message and delegates to the right specialist. Never answers directly — always coordinates.

2. **📚 The Librarian:** The Wiki specialist. Equipped with `search_wiki` to query your local ChromaDB vector store, finding relevant context from every PDF you've ever uploaded.

3. **🌐 The Researcher:** The Internet crawler. Equipped with `search_web` (DuckDuckGo) and `scrape_website` (BeautifulSoup4) to find and deeply read live web articles.

4. **📋 The Project Manager:** The Data Entry expert. Equipped with `save_action_item`, `save_idea`, `save_note`, `get_pending_tasks`, and `search_ideas` to seamlessly read and write directly to your SQLite database.

5. **📊 The Analyst:** The math and logic specialist. Equipped with `run_python` — an isolated code sandbox — for 100% flawless calculations and data analysis.

6. **🗓️ The Executive Assistant *(NEW)*:** Your personal Google Workspace assistant. Equipped with 4 tools:
   - `check_google_calendar(date)` — Check your schedule for any day
   - `create_google_calendar_event(...)` — Block time and create meetings
   - `read_recent_emails()` — Scan your unread Gmail inbox
   - `search_gmail(query)` — Find any email thread using Gmail search syntax

---

## 👁️ Multimodal Intelligence (Vision & Voice)

Beyond text, your WhatsApp bot now accepts rich media:
- **📸 Image Messages:** Send a photo of a whiteboard, book page, or receipt. GPT-4o Vision will read and analyze it, then pass the insights to the right agent.
- **🎙️ Voice Notes:** Record a voice note while driving. Whisper-1 transcribes it instantly and routes it to the Supervisor.

---

## 💻 Premium Web Dashboard

- **Animated Background:** Slowly drifting ambient light orbs (blue, purple, cyan) for a premium deep-space aesthetic.
- **Live Clock:** Real-time date and time displayed in the dashboard header.
- **Type-Specific Glow:** Memory cards cast colored neon glows on hover: Knowledge = blue, Actions = orange, Ideas = green.
- **Staggered Animations:** Memory cards cascade into view with staggered fade-in timing.
- **🔗 Semantic Wiki Connectivity:** Every Knowledge article automatically shows "Connected Knowledge" — AI-computed links to related articles using ChromaDB vector similarity.
- **Split-Screen PDF View:** Read AI-generated summaries alongside the embedded original PDF.
- **Dynamic Search & Filtering:** Instant search across your entire knowledge base.

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Andrariando/SecondBrain.git
cd SecondBrain/second-brain-agent
```

### 2. Create & Activate Virtual Environment
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
```bash
cp .env.example .env
# Then edit .env and fill in your keys
```

### 5. Google Workspace Setup *(Optional — for Executive Assistant)*
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a project → Enable **Gmail API** and **Google Calendar API**
3. Create **OAuth 2.0 credentials** → Download as `credentials.json` into the project root
4. Run the one-time auth script:
   ```bash
   python app/google_auth.py
   ```
   A browser window will open. Log in and authorize. This generates `token.json` automatically.

---

## 🏃 Running the Application

```bash
uvicorn app.main:app --reload --port 8000
```
Access the Web Dashboard at **[http://localhost:8000](http://localhost:8000)**

For WhatsApp webhook, expose localhost with ngrok:
```bash
ngrok http 8000
```
Configure your Meta WhatsApp Webhook URL to: `https://<ngrok-url>/whatsapp`
