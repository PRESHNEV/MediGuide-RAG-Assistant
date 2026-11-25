# MediGuide — Medical Knowledge RAG Assistant

A runnable document-grounded RAG demo. It ingests PDF/TXT files, chunks text, retrieves relevant passages with TF-IDF, and returns source references. An optional OpenAI-compatible LLM endpoint can synthesize answers. Without an LLM key, it runs in retrieval-only mode.

**Safety:** educational software demo only; not a diagnostic tool or medical advice. Do not upload private patient data.

## Windows / VS Code setup
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.api:app --reload
```
Open another terminal in this folder:
```powershell
.\.venv\Scripts\Activate.ps1
streamlit run ui/streamlit_app.py
```
API docs: http://127.0.0.1:8000/docs

Add trusted PDF/TXT files to `data/knowledge_base/`, then click Re-index. Run tests with `pytest -q`.

Optional LLM: fill `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL` in `.env` using an OpenAI-compatible chat-completions endpoint. Never commit `.env`.
