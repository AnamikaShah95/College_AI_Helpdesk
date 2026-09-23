# College AI Helpdesk — Domain Verse 1.0

A lightweight Agentic AI college helpdesk for PS-02.

## Stack
- Python
- Streamlit
- LangGraph
- Gemini
- SQLite
- Structured JSON knowledge base

## Setup
1. Create a virtual environment.
2. Install requirements:
   `pip install -r requirements.txt`
3. Copy `.env.example` to `.env`.
4. Add your Gemini API key to `.env`.
5. Run:
   `streamlit run app.py`

## Important
The included knowledge base contains only verified/sample records that are clearly marked. Add actual college documents/data before claiming information is verified.

The application follows:
QUESTION -> CONTEXT -> PLAN -> TOOL/RETRIEVAL -> VERIFY -> REPLAN IF NEEDED -> ANSWER + SOURCES
