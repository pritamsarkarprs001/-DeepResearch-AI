# agents/researcher.py
# RESEARCHER AGENT: Gathers info from documents (RAG) + Wikipedia API + DuckDuckGo (fallback)

import time
import requests
from duckduckgo_search import DDGS
from agents.llm_config import get_llm
from rag.retriever import retrieve_relevant_chunks


def wikipedia_search(query: str) -> list:
    """
    Search Wikipedia using their FREE public API directly.
    No library needed, no rate limits, no API key.
    Returns a list with one result dict (title, snippet, url).
    """
    try:
        # Step 1: Search for the best matching Wikipedia article title
        search_url = "https://en.wikipedia.org/w/api.php"
        search_params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json",
            "srlimit": 1  # just get the top result
        }
        headers = {"User-Agent": "DeepResearchAI/1.0 (portfolio project)"}

        search_resp = requests.get(search_url, params=search_params, headers=headers, timeout=10)
        search_data = search_resp.json()

        results = search_data.get("query", {}).get("search", [])
        if not results:
            print(f"⚠️ Wikipedia: no results found for '{query}'")
            return []

        # Get the top result's page title
        top_title = results[0]["title"]

        # Step 2: Get the actual page summary using the title
        summary_params = {
            "action": "query",
            "prop": "extracts",
            "exintro": True,          # only get the intro section
            "explaintext": True,      # plain text, no HTML
            "titles": top_title,
            "format": "json"
        }

        summary_resp = requests.get(search_url, params=summary_params, headers=headers, timeout=10)
        summary_data = summary_resp.json()

        pages = summary_data.get("query", {}).get("pages", {})
        page = next(iter(pages.values()))  # get the first (only) page

        extract = page.get("extract", "")
        if not extract:
            return []

        # Trim to first 800 characters so we don't flood the AI context
        short_extract = extract[:800] + "..." if len(extract) > 800 else extract

        page_url = f"https://en.wikipedia.org/wiki/{top_title.replace(' ', '_')}"
        print(f"✅ Wikipedia found: '{top_title}'")

        return [{
            "title": f"Wikipedia: {top_title}",
            "snippet": short_extract,
            "url": page_url
        }]

    except Exception as e:
        print(f"⚠️ Wikipedia API error for '{query}': {e}")
        return []


def duckduckgo_search(query: str, max_results: int = 2) -> list:
    """
    DuckDuckGo as a bonus search (may fail due to rate limits — that's okay).
    Wikipedia is our main source so DuckDuckGo failure doesn't matter.
    """
    backends = ["html", "lite", "api"]
    for backend in backends:
        try:
            time.sleep(3)
            with DDGS() as ddgs:
                results = list(ddgs.text(
                    query,
                    max_results=max_results,
                    backend=backend
                ))
                if results:
                    print(f"✅ DuckDuckGo succeeded with '{backend}' backend.")
                    return [
                        {
                            "title": r.get("title", ""),
                            "snippet": r.get("body", ""),
                            "url": r.get("href", "")
                        }
                        for r in results
                    ]
        except Exception as e:
            print(f"⚠️ DuckDuckGo '{backend}' failed: {e}")
            time.sleep(2)

    print("⚠️ DuckDuckGo unavailable — using Wikipedia only.")
    return []


def web_search(query: str) -> list:
    """
    Main search: Wikipedia first (always reliable), DuckDuckGo as bonus.
    """
    results = []
    results.extend(wikipedia_search(query))   # primary — always works
    results.extend(duckduckgo_search(query))  # bonus — may fail silently
    return results


def researcher_agent(sub_questions: list) -> list:
    """
    Input: list of sub-questions from Planner
    Output: list of research notes, each with a summary + sources
    """
    llm = get_llm(temperature=0.2)
    notes = []

    for question in sub_questions:
        print(f"\n🔍 Researching: {question}")

        # 1. Search uploaded documents (local RAG)
        doc_chunks = retrieve_relevant_chunks(question, k=3)

        # 2. Search the web (Wikipedia + DuckDuckGo)
        web_results = web_search(question)

        # 3. Combine both sources into one context block
        context_text = ""
        sources = []

        for chunk in doc_chunks:
            context_text += f"[Document: {chunk['source']}, page {chunk['page']}]\n{chunk['text']}\n\n"
            sources.append({
                "type": "document",
                "ref": f"{chunk['source']} (p.{chunk['page']})"
            })

        for res in web_results:
            context_text += f"[Web: {res['title']}]\n{res['snippet']}\n\n"
            sources.append({
                "type": "web",
                "ref": res["title"],
                "url": res["url"]
            })

        # If nothing found at all, skip AI call
        if not context_text.strip():
            notes.append({
                "question": question,
                "summary": "No information found.",
                "sources": []
            })
            continue

        # 4. Ask AI to summarize findings for this sub-question
        prompt = f"""Based ONLY on the context below, write a clear, factual 3-4 sentence
summary answering this question: "{question}"

Context:
{context_text}

Summary:"""

        try:
            response = llm.invoke(prompt)
            summary = response.content.strip()
        except Exception as e:
            print(f"❌ Researcher summarization error: {e}")
            summary = "Could not generate summary due to an error."

        notes.append({
            "question": question,
            "summary": summary,
            "sources": sources
        })

    return notes