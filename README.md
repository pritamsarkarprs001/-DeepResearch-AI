# 🔍 DeepResearch AI
**Adaptive Multi-Agent Research & Report Generator**


> Turn any research topic into a fully written, cited report in minutes — powered entirely by free, open-source tools.

---

## 📌 Live Demo
👉 **[Try DeepResearch AI](https://YOUR-APP-URL.streamlit.app)**

---

## 🎯 What It Does

| Feature | Description |
|---|---|
| 📁 Document Upload | Upload PDFs and index them locally into ChromaDB |
| 💬 Chat Interface | Ask questions about your documents using RAG |
| 🤖 Multi-Agent Report | 4 agents research, review, and write a full report |
| 🌐 Live Web Search | Searches Wikipedia + DuckDuckGo automatically |
| 📄 PDF Download | One-click export of the final report |

---

## 🤖 How the Agent Pipeline Works

```
User enters a topic
        │
        ▼
┌─────────────────┐
│  🧠 PLANNER     │  Breaks topic into 4 focused sub-questions
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  🔎 RESEARCHER  │  Searches documents (RAG) + Wikipedia + DuckDuckGo
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  🧐 CRITIC      │  Reviews quality — loops back if gaps found
└────────┬────────┘
         │
    ┌────┴─────┐
    │ Approved? │
    └────┬─────┘
    Yes  │  No → back to Researcher (max 2 loops)
         ▼
┌─────────────────┐
│ ✍️ SYNTHESIZER  │  Writes full structured report with citations
└────────┬────────┘
         │
         ▼
   📄 PDF Download
```

---

## 🛠️ Tech Stack

| Layer | Technology | Cost |
|---|---|---|
| UI | Streamlit | Free |
| LLM | Groq API — Llama 3.1 8B | Free tier |
| Agent Orchestration | LangGraph | Free |
| RAG Framework | LangChain | Free |
| Vector Database | ChromaDB (local) | Free |
| Embeddings | Sentence Transformers (all-MiniLM-L6-v2) | Free |
| Web Search | Wikipedia API + DuckDuckGo | Free |
| PDF Generation | pdfkit + wkhtmltopdf | Free |
| PDF Parsing | PyPDF | Free |

**Total cost to run: $0**

---

## 📁 Project Structure

```
deepresearch-ai/
├── app.py                    # Main Streamlit UI
├── requirements.txt          # Python dependencies
├── packages.txt              # System packages (Streamlit Cloud)
├── .env                      # Your API key (not uploaded to GitHub)
│
├── agents/
│   ├── llm_config.py         # Shared Groq LLM connection
│   ├── planner.py            # Breaks topic into sub-questions
│   ├── researcher.py         # Searches docs + web
│   ├── critic.py             # Reviews research quality
│   ├── synthesizer.py        # Writes the final report
│   └── graph.py              # LangGraph workflow (the pipeline)
│
├── rag/
│   ├── indexer.py            # PDF → ChromaDB vector store
│   └── retriever.py          # Semantic search over documents
│
└── utils/
    └── report_generator.py   # Markdown → PDF converter
```

---

## ⚡ Local Setup

### Requirements
- Python 3.11+
- Free Groq API key → [console.groq.com](https://console.groq.com)
- [wkhtmltopdf](https://wkhtmltopdf.org/downloads.html) (for PDF export)

### Steps

```bash
# 1. Clone the repo
git clone https://github.com/YourUsername/deepresearch-ai.git
cd deepresearch-ai

# 2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file and add your Groq key
echo GROQ_API_KEY=your_key_here > .env

# 5. Run the app
streamlit run app.py
```

Then open your browser to: `http://localhost:8501`

---

## ☁️ Deploy on Streamlit Cloud (Free)

1. Fork this repository
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Select your forked repo, branch `main`, file `app.py`
4. Under **Advanced settings → Secrets**, add:
```toml
GROQ_API_KEY = "your_groq_api_key_here"
```
5. Click **Deploy** — live in ~3 minutes

---

## 💡 Skills Demonstrated

- ✅ **RAG Pipeline** — PDF ingestion, chunking, embedding, semantic retrieval
- ✅ **Multi-Agent Design** — 4 specialized agents with defined roles
- ✅ **LangGraph State Machines** — conditional edges, looping, shared state
- ✅ **Tool Use** — agents call Wikipedia and DuckDuckGo at runtime
- ✅ **Free LLM Integration** — Groq API with Llama 3.1
- ✅ **Vector Databases** — ChromaDB with local persistence
- ✅ **Production UI** — Streamlit with tabs, chat, progress, file upload

---

## 🖼️ Screenshots

> Add screenshots of your running app here.
> Press `Win + Shift + S` to screenshot, then drag the image into this README on GitHub.

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

---

## 📄 License

[MIT](LICENSE) — free to use, modify, and share.

---

<p align="center">Built with ❤️ using free tools only · No paid APIs · Total cost: $0</p>