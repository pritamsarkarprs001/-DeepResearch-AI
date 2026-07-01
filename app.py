# app.py - Main Streamlit App for DeepResearch AI

import streamlit as st
import os
from rag.indexer import index_documents
from rag.retriever import retrieve_relevant_chunks
from agents.llm_config import get_llm
from agents.graph import build_research_graph
from utils.report_generator import generate_pdf_report, generate_markdown_file

# ---- Page setup ----
st.set_page_config(page_title="DeepResearch AI", layout="wide")
st.title("🔍 DeepResearch AI")
st.caption("Adaptive Multi-Agent Research & Report Generator")

# ---- Session state ----
if "indexed_files" not in st.session_state:
    st.session_state.indexed_files = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "report_result" not in st.session_state:
    st.session_state.report_result = None  # stores final pipeline output

# ---- Sidebar: Document Upload ----
with st.sidebar:
    st.header("📁 Upload Documents")
    st.write("Upload PDFs to let the AI search them during research.")

    uploaded_files = st.file_uploader("Choose PDF files", type=["pdf"], accept_multiple_files=True)

    if uploaded_files and st.button("📥 Index Documents"):
        saved_paths = []
        with st.spinner("Saving and indexing documents..."):
            for file in uploaded_files:
                save_path = os.path.join("data", file.name)
                with open(save_path, "wb") as f:
                    f.write(file.getbuffer())
                saved_paths.append(save_path)
            try:
                index_documents(saved_paths)
                st.session_state.indexed_files.extend([f.name for f in uploaded_files])
                st.success(f"✅ Indexed {len(saved_paths)} document(s) successfully!")
            except Exception as e:
                st.error(f"❌ Indexing failed: {e}")

    if st.session_state.indexed_files:
        st.write("**Indexed files:**")
        for fname in st.session_state.indexed_files:
            st.write(f"✅ {fname}")


def answer_question(question: str) -> str:
    """Simple RAG: retrieve relevant chunks, then ask the AI to answer using them."""
    chunks = retrieve_relevant_chunks(question, k=4)
    if not chunks:
        return "⚠️ No indexed documents found, or nothing relevant. Try uploading a document first."

    context = "\n\n".join([f"[{c['source']} p.{c['page']}]\n{c['text']}" for c in chunks])
    prompt = f"""Answer the question using ONLY the context below. Be concise.
If the answer isn't in the context, say so honestly.

Context:
{context}

Question: {question}

Answer:"""
    try:
        llm = get_llm(temperature=0.2)
        response = llm.invoke(prompt)
        return response.content.strip()
    except Exception as e:
        return f"❌ Error generating answer: {e}"


# ---- Main area: Tabs ----
tab_chat, tab_report = st.tabs(["💬 Chat", "📊 Full Report"])

# === CHAT TAB ===
with tab_chat:
    st.subheader("Chat with your documents")

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_input = st.chat_input("Ask a question about your uploaded documents...")

    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer = answer_question(user_input)
                st.write(answer)
        st.session_state.chat_history.append({"role": "assistant", "content": answer})

# === FULL REPORT TAB ===
with tab_report:
    st.subheader("Generate a Full Research Report")
    st.write("Our 4 AI agents will plan, research (documents + live web), critique, and write a complete report.")

    topic = st.text_input("Enter your research topic:", placeholder="e.g. Impact of AI on the job market")
    generate_clicked = st.button("🚀 Generate Full Report", type="primary")

    if generate_clicked and topic.strip():
        initial_state = {
            "topic": topic,
            "sub_questions": [],
            "research_notes": [],
            "critique": {},
            "iteration": 0,
            "final_report": "",
            "status": "Starting..."
        }

        app_graph = build_research_graph()
        final_state = initial_state

        # st.status gives a nice live-updating progress box
        with st.status("Running multi-agent pipeline...", expanded=True) as status_box:
            try:
                # stream_mode="values" gives us the FULL state after each agent runs
                for state_update in app_graph.stream(initial_state, stream_mode="values"):
                    final_state = state_update
                    status_box.write(final_state.get("status", "Working..."))
                status_box.update(label="✅ Pipeline complete!", state="complete")
            except Exception as e:
                status_box.update(label=f"❌ Pipeline failed: {e}", state="error")

        st.session_state.report_result = final_state

    # ---- Display the report if we have one ----
    result = st.session_state.report_result
    if result and result.get("final_report"):
        st.write("---")
        st.markdown(result["final_report"])

        # Show research process details in an expandable section
        with st.expander("🔍 View research process details"):
            st.write("**Sub-questions researched:**")
            for q in result.get("sub_questions", []):
                st.write(f"- {q}")
            st.write("**Critic feedback:**", result.get("critique", {}).get("feedback", "N/A"))

        # ---- PDF Download ----
        if st.button("📄 Prepare PDF Download"):
            with st.spinner("Generating PDF..."):
                pdf_path = generate_pdf_report(result["final_report"], "report.pdf")
                if pdf_path and os.path.exists(pdf_path):
                    with open(pdf_path, "rb") as f:
                        st.download_button(
                            label="⬇️ Download Report PDF",
                            data=f.read(),
                            file_name="DeepResearch_Report.pdf",
                            mime="application/pdf"
                        )
                else:
                    # Fallback: offer markdown download instead
                    md_path = generate_markdown_file(result["final_report"], "report.md")
                    with open(md_path, "r", encoding="utf-8") as f:
                        st.download_button(
                            label="⬇️ Download Report (Markdown)",
                            data=f.read(),
                            file_name="DeepResearch_Report.md",
                            mime="text/markdown"
                        )
                    st.warning("PDF generation failed, so we gave you a Markdown file instead.")