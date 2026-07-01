# 🚀 DeepResearch AI — Complete Deployment Guide
### GitHub + Streamlit Cloud + LinkedIn Portfolio

---

## 📋 Table of Contents
1. [Fix Dependency Issues](#1-fix-dependency-issues-do-this-first)
2. [Prepare Files for Deployment](#2-prepare-files-for-deployment)
3. [Create GitHub Account & Repository](#3-create-github-account--repository)
4. [Push Code to GitHub](#4-push-code-to-github)
5. [Deploy on Streamlit Community Cloud (Free)](#5-deploy-on-streamlit-community-cloud-free)
6. [Update README for Portfolio](#6-update-readme-for-portfolio)
7. [LinkedIn Post Guide](#7-linkedin-post-guide)
8. [Resume Description](#8-resume-description)

---

## 1. Fix Dependency Issues (Do This First)

Your terminal showed version conflicts. We must fix these before deploying or the cloud server will fail to build.

### Step 1.1 — Uninstall conflicting packages

Open VS Code terminal (make sure you see `(venv)`) and run:

```bash
pip uninstall wikipedia-api tenacity click langchain langchain-community langchain-groq langchain-chroma langgraph langchain-core langsmith langchain-huggingface langchain-text-splitters streamlit -y
```

Wait for it to finish (you will see "Successfully uninstalled..." messages).

### Step 1.2 — Reinstall everything with pinned compatible versions

Copy and paste this entire block at once:

```bash
pip install streamlit==1.38.0 langchain==0.3.7 langchain-community==0.3.5 langchain-groq==0.2.1 langgraph==0.2.45 chromadb==0.5.18 sentence-transformers==3.2.1 duckduckgo-search==6.3.5 pypdf==5.1.0 python-dotenv==1.0.1 markdown==3.7 pdfkit==1.0.0 langchain-chroma==0.1.4 langchain-huggingface==0.1.0 lxml requests
```

Wait for it to finish (2–5 minutes). You should see no red ERROR lines at the end.

### Step 1.3 — Verify everything works

Run:

```bash
python -c "import streamlit, langchain, langgraph, chromadb; print('✅ All packages OK')"
```

Expected output: `✅ All packages OK`

### Step 1.4 — Freeze your exact working versions

```bash
pip freeze > requirements.txt
```

This overwrites `requirements.txt` with your EXACT working versions so the cloud server installs the same thing.

---

## 2. Prepare Files for Deployment

Cloud servers cannot use your local `.env` file (it is secret and not uploaded to GitHub). We handle this with Streamlit's Secrets system. But first, we prepare some files.

### Step 2.1 — Create `.gitignore`

If you already have it, open it. Replace everything with this:

```
# Virtual environment (huge, not needed on cloud)
venv/

# Secret keys — NEVER upload this
.env

# Local database (too large, rebuilt on cloud)
chroma_db/

# Uploaded PDFs (user files, private)
data/*.pdf

# Python cache files
__pycache__/
*.pyc
*.pyo
.pytest_cache/

# Generated reports
*.pdf
report.md

# OS files
.DS_Store
Thumbs.db
```

Save: `Ctrl + S`

### Step 2.2 — Create `packages.txt` (for wkhtmltopdf on cloud)

The cloud server runs Linux. We need to tell it to install wkhtmltopdf automatically.

Right-click the sidebar → New File → name it `packages.txt`

Paste this inside:

```
wkhtmltopdf
```

Save: `Ctrl + S`

### Step 2.3 — Update `utils/report_generator.py` to auto-detect environment

On the cloud, wkhtmltopdf is in a different location than Windows. Open `utils/report_generator.py`, select all, delete, paste:

```python
# utils/report_generator.py
# Converts our Markdown research report into a styled, downloadable PDF.
# Auto-detects whether we are running locally (Windows) or on Streamlit Cloud (Linux).

import markdown
import pdfkit
import os
import shutil

# Auto-detect where wkhtmltopdf is installed
def get_wkhtmltopdf_path():
    """Find wkhtmltopdf automatically on any OS."""
    # Try system PATH first (works on Linux/Streamlit Cloud)
    system_path = shutil.which("wkhtmltopdf")
    if system_path:
        return system_path

    # Fallback: Windows default install location
    windows_path = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
    if os.path.exists(windows_path):
        return windows_path

    return None


# Basic CSS so the PDF looks clean and professional
REPORT_CSS = """
<style>
    body {
        font-family: Arial, sans-serif;
        line-height: 1.6;
        color: #222;
        padding: 30px;
        max-width: 800px;
        margin: 0 auto;
    }
    h1 { color: #1a4d8f; border-bottom: 2px solid #1a4d8f; padding-bottom: 8px; }
    h2 { color: #2c6cb5; margin-top: 25px; }
    h3 { color: #3a7fc1; }
    li { margin-bottom: 6px; }
    a { color: #1a4d8f; }
    p { margin-bottom: 12px; }
</style>
"""


def markdown_to_html(markdown_text: str) -> str:
    """Convert Markdown text into full styled HTML."""
    body_html = markdown.markdown(markdown_text, extensions=["extra"])
    full_html = f"<html><head>{REPORT_CSS}</head><body>{body_html}</body></html>"
    return full_html


def generate_pdf_report(markdown_text: str, output_path: str = "report.pdf") -> str:
    """
    Converts markdown -> styled HTML -> PDF.
    Returns the output_path if successful, or None if it failed.
    """
    try:
        wkhtmltopdf_path = get_wkhtmltopdf_path()

        if not wkhtmltopdf_path:
            print("⚠️ wkhtmltopdf not found. Falling back to Markdown.")
            return None

        html_content = markdown_to_html(markdown_text)
        config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
        options = {
            "encoding": "UTF-8",
            "enable-local-file-access": None,
        }

        pdfkit.from_string(html_content, output_path, configuration=config, options=options)
        print(f"✅ PDF saved to {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ PDF generation failed: {e}")
        return None


def generate_markdown_file(markdown_text: str, output_path: str = "report.md") -> str:
    """Fallback: save as plain Markdown file (always works, no dependencies)."""
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown_text)
        print(f"✅ Markdown saved to {output_path}")
        return output_path
    except Exception as e:
        print(f"❌ Markdown save failed: {e}")
        return None
```

Save: `Ctrl + S`

### Step 2.4 — Update `app.py` to read Groq key from Streamlit Secrets (cloud) OR `.env` (local)

Open `app.py`. Find the imports at the very top. Make sure these lines are there:

```python
import streamlit as st
import os
from dotenv import load_dotenv

# Load .env for local development
load_dotenv()

# If running on Streamlit Cloud, inject the secret into environment
if "GROQ_API_KEY" in st.secrets:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
```

Add these lines **right after** `import streamlit as st` at the very top of `app.py`, before all other imports. Keep the rest of `app.py` exactly as it was.

Save: `Ctrl + S`

### Step 2.5 — Create `data/.gitkeep`

The `data/` folder must exist on the cloud but be empty. Run in terminal:

```bash
type nul > data\.gitkeep
```

---

## 3. Create GitHub Account & Repository

### Step 3.1 — Create a free GitHub account

1. Go to: `https://github.com`
2. Click **Sign up** (top right).
3. Enter your email → create password → choose username.
4. Verify your email.

### Step 3.2 — Install Git (if not already installed)

1. Go to: `https://git-scm.com/download/win`
2. Click the first download link (latest version).
3. Run the installer → click **Next** through everything (all defaults are fine).
4. When done, close and reopen your VS Code terminal.
5. Verify:

```bash
git --version
```

Expected: `git version 2.x.x`

### Step 3.3 — Configure Git with your identity

Run these two commands (replace with YOUR name and email):

```bash
git config --global user.name "Your Name Here"
```

```bash
git config --global user.email "youremail@example.com"
```

### Step 3.4 — Create a new repository on GitHub

1. Go to: `https://github.com/new`
2. Fill in:
   - **Repository name:** `deepresearch-ai`
   - **Description:** `Multi-Agent RAG Research & Report Generator — Built with LangGraph, Groq, ChromaDB, Streamlit`
   - **Visibility:** ✅ Public (required for free Streamlit Cloud deployment)
   - **Do NOT check** "Add README" or "Add .gitignore" (we already have them)
3. Click **Create repository**.
4. Leave this page open — you will need the URL shown.

---

## 4. Push Code to GitHub

Run these commands in your VS Code terminal **one at a time**:

### Step 4.1 — Initialize Git in your project

```bash
git init
```

### Step 4.2 — Add all files

```bash
git add .
```

### Step 4.3 — Make your first commit

```bash
git commit -m "Initial commit: DeepResearch AI - Multi-Agent RAG Research Generator"
```

### Step 4.4 — Set main branch name

```bash
git branch -M main
```

### Step 4.5 — Connect to your GitHub repository

Copy the URL from the GitHub page you left open. It looks like:
`https://github.com/YourUsername/deepresearch-ai.git`

Run (replace with YOUR actual URL):

```bash
git remote add origin https://github.com/YourUsername/deepresearch-ai.git
```

### Step 4.6 — Push your code

```bash
git push -u origin main
```

GitHub will ask for your username and password. For the **password**, you must use a Personal Access Token, NOT your GitHub password:

1. Go to: `https://github.com/settings/tokens`
2. Click **Generate new token (classic)**
3. Give it a name (e.g. `deepresearch`)
4. Check ✅ **repo** scope
5. Click **Generate token**
6. Copy the token (starts with `ghp_...`) — paste it as the password

### Step 4.7 — Verify it worked

Go to `https://github.com/YourUsername/deepresearch-ai` in your browser.

✅ You should see all your project files listed there.

---

## 5. Deploy on Streamlit Community Cloud (Free)

Streamlit Cloud is 100% free and hosts your app permanently with a public URL.

### Step 5.1 — Create Streamlit Cloud account

1. Go to: `https://share.streamlit.io`
2. Click **Sign up with GitHub** — this links your account automatically.
3. Authorize Streamlit to access your GitHub.

### Step 5.2 — Deploy your app

1. Click **New app** (top right).
2. Fill in:
   - **Repository:** `YourUsername/deepresearch-ai`
   - **Branch:** `main`
   - **Main file path:** `app.py`
3. Click **Advanced settings**.
4. Under **Secrets**, paste this (replace with your actual key):

```toml
GROQ_API_KEY = "gsk_your_actual_key_here"
```

5. Click **Save** → then click **Deploy**.

### Step 5.3 — Wait for build

The first build takes **3–5 minutes**. You will see a log of packages being installed.

✅ When done, your app appears at a URL like:
`https://yourname-deepresearch-ai-app-xxxx.streamlit.app`

**Save this URL — this is your live portfolio link!**

### Step 5.4 — If the build fails

Common fixes:

- **ModuleNotFoundError** → check `requirements.txt` has all packages
- **GROQ_API_KEY not found** → re-check the Secrets section in Step 5.2
- **wkhtmltopdf error** → check `packages.txt` file exists with `wkhtmltopdf` inside

To view logs: click **Manage app** (bottom right of the running app) → **Logs**

---

## 6. Update README for Portfolio

Open `README.md`, select all, delete, paste this full professional version:

```markdown
# 🔍 DeepResearch AI
### Adaptive Multi-Agent Research & Report Generator

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://YOUR-APP-URL.streamlit.app)

> Built entirely with **free, open-source tools** — no paid APIs. Demonstrates RAG, multi-agent orchestration, tool use, and a production-ready Streamlit UI.

---

## 🎯 What It Does

DeepResearch AI is a production-style AI research assistant powered by a 4-agent LangGraph pipeline.

1. Upload your own PDF documents (research papers, reports, textbooks)
2. Chat with them instantly using RAG-powered Q&A
3. Enter any research topic → click one button → get a full written report in seconds
4. Download the report as a PDF

---

## 🤖 The Multi-Agent Pipeline

```
Topic Input
    │
    ▼
🧠 PLANNER AGENT
Breaks topic into 4 focused sub-questions
    │
    ▼
🔎 RESEARCHER AGENT
Searches: Your uploaded documents (RAG) + Wikipedia + DuckDuckGo
    │
    ▼
🧐 CRITIC AGENT
Reviews quality. Loops back if gaps found (max 2 iterations)
    │
    ▼
✍️ SYNTHESIZER AGENT
Writes structured report with citations
    │
    ▼
📄 PDF Download
```

---

## 🛠️ Tech Stack (All Free & Open Source)

| Component | Technology |
|-----------|-----------|
| UI | Streamlit |
| LLM | Groq API — Llama 3.1 8B (free tier) |
| Agent Orchestration | LangGraph |
| RAG Framework | LangChain |
| Vector Database | ChromaDB (local) |
| Embeddings | Sentence Transformers (all-MiniLM-L6-v2) |
| Web Search | Wikipedia API + DuckDuckGo |
| PDF Generation | pdfkit + wkhtmltopdf |
| PDF Reading | PyPDF |

---

## 📁 Project Structure

```
deepresearch-ai/
├── app.py                    # Main Streamlit app
├── requirements.txt          # Python dependencies
├── packages.txt              # System packages (for Streamlit Cloud)
├── agents/
│   ├── llm_config.py         # Shared Groq LLM connector
│   ├── planner.py            # Planner agent
│   ├── researcher.py         # Researcher agent (RAG + web search)
│   ├── critic.py             # Critic / quality checker agent
│   ├── synthesizer.py        # Report writer agent
│   └── graph.py              # LangGraph multi-agent workflow
├── rag/
│   ├── indexer.py            # PDF → ChromaDB indexer
│   └── retriever.py          # Semantic search retriever
├── utils/
│   └── report_generator.py   # Markdown → PDF converter
└── data/                     # Uploaded documents (local only)
```

---

## ⚡ Quick Start (Local)

### Prerequisites
- Python 3.11+
- Free Groq API key from https://console.groq.com
- wkhtmltopdf installed (for PDF export)

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/YourUsername/deepresearch-ai.git
cd deepresearch-ai

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your Groq API key
echo GROQ_API_KEY=your_key_here > .env

# 5. Run the app
streamlit run app.py
```

Open your browser to `http://localhost:8501`

---

## 🌐 Live Demo

👉 **[Try it live here](https://YOUR-APP-URL.streamlit.app)**

---

## 💡 Key Technical Concepts Demonstrated

- **Retrieval-Augmented Generation (RAG):** Documents are chunked, embedded with Sentence Transformers, stored in ChromaDB, and retrieved semantically at query time.
- **Multi-Agent Orchestration (LangGraph):** A stateful graph wires four specialized agents, with conditional edges allowing the Critic to trigger re-research loops.
- **Tool Use:** The Researcher agent dynamically calls Wikipedia and DuckDuckGo as external tools during runtime.
- **State Management:** LangGraph's `TypedDict` state flows between agents, accumulating research notes and triggering decisions.
- **Free LLM Integration:** Groq's free tier provides extremely fast Llama 3.1 inference with no cost.

---

## 📸 Screenshots

> *(Add screenshots of your running app here after deployment)*

---

## 📝 License

MIT License — free to use, modify, and share.
```

Save: `Ctrl + S`

**Important:** Replace `YOUR-APP-URL` in two places with your actual Streamlit URL from Step 5.3.

Then push the updated README:

```bash
git add README.md
git commit -m "Add professional README with live demo link"
git push
```

---

## 7. LinkedIn Post Guide

Use this template to announce your project. Edit the personal parts:

---

**Suggested LinkedIn Post:**

```
🚀 I just built and deployed a full Multi-Agent AI Research System — 
using only FREE tools!

DeepResearch AI is a RAG + LangGraph-powered app that:

🧠 PLANNER → breaks your topic into sub-questions
🔎 RESEARCHER → searches your documents + the live web
🧐 CRITIC → reviews quality and loops back if needed
✍️ SYNTHESIZER → writes a full cited research report
📄 One-click PDF download

Tech stack (all 100% free):
• Groq API (Llama 3.1 — blazing fast, free tier)
• LangGraph (multi-agent orchestration)
• ChromaDB (local vector database)
• Sentence Transformers (embeddings)
• Wikipedia + DuckDuckGo (live web search)
• Streamlit (UI)

This project demonstrates skills I see in real AI engineering job descriptions:
✅ RAG pipelines
✅ Agent design patterns
✅ LangGraph state machines
✅ Vector databases
✅ Production Streamlit apps

🔗 Live demo: [YOUR STREAMLIT URL]
💻 GitHub: [YOUR GITHUB URL]

Built this as a portfolio project while learning AI engineering.
Happy to answer any questions about how it works!

#AI #MachineLearning #LLM #RAG #LangChain #Python #Portfolio
#AIEngineering #OpenSource #Streamlit #GenerativeAI
```

---

**LinkedIn Profile Tips:**

1. **Add to Featured section:**
   - Go to your LinkedIn profile
   - Click "Add profile section" → Featured → Add a link
   - Paste your Streamlit app URL
   - Title: "DeepResearch AI — Multi-Agent Research System"

2. **Add to Projects section:**
   - "Add profile section" → Additional → Projects
   - Project name: `DeepResearch AI`
   - Description: Copy the first paragraph from your README
   - Project URL: Your Streamlit app URL

3. **Update your About section** to mention: "Building AI systems with RAG, LangGraph, and LLMs."

---

## 8. Resume Description

Use this in your CV under Projects:

```
DeepResearch AI — Multi-Agent RAG Research Generator          [GitHub] [Live Demo]
• Built a production-ready AI research system using LangGraph to orchestrate a 
  4-agent pipeline (Planner → Researcher → Critic → Synthesizer) with 
  conditional re-research loops based on quality critique.
• Implemented RAG using ChromaDB vector store and Sentence Transformers embeddings,
  enabling semantic search over user-uploaded PDF documents.
• Integrated free Groq API (Llama 3.1 8B) for LLM inference and Wikipedia/DuckDuckGo
  for live web research as agent tools.
• Deployed full-stack Streamlit application on Streamlit Community Cloud with 
  one-click PDF report generation and real-time agent progress tracking.
• Tech: Python, LangGraph, LangChain, ChromaDB, Groq API, Streamlit, Sentence Transformers
```

---

## ✅ Deployment Checklist

Before sharing your links publicly, verify all of these:

- [ ] `pip freeze > requirements.txt` saved correctly
- [ ] `.gitignore` includes `.env` and `venv/`
- [ ] `packages.txt` exists with `wkhtmltopdf`
- [ ] Streamlit Secrets has your `GROQ_API_KEY`
- [ ] App builds successfully on Streamlit Cloud (no red errors)
- [ ] Live app: can upload a PDF and index it
- [ ] Live app: chat tab returns answers
- [ ] Live app: report tab generates a full report
- [ ] Live app: PDF download works (or Markdown fallback works)
- [ ] README has correct live demo URL
- [ ] GitHub repository is set to Public

---

*DeepResearch AI — Portfolio Project Guide*
*Built with free tools: Groq, LangGraph, ChromaDB, Streamlit*
