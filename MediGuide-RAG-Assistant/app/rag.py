import re
import requests
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.config import KNOWLEDGE_DIR, LLM_BASE_URL, LLM_API_KEY, LLM_MODEL

class RAGEngine:
    def __init__(self):
        self.chunks, self.vectorizer, self.matrix = [], None, None

    def _read(self, path):
        if path.suffix.lower() == ".txt":
            return [(None, path.read_text(encoding="utf-8", errors="ignore"))]
        if path.suffix.lower() == ".pdf":
            return [(i + 1, p.extract_text() or "") for i, p in enumerate(PdfReader(str(path)).pages)]
        return []

    def ingest(self):
        KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
        self.chunks = []
        for path in KNOWLEDGE_DIR.iterdir():
            if path.suffix.lower() not in {".txt", ".pdf"}:
                continue
            for page, text in self._read(path):
                text = re.sub(r"\\s+", " ", text).strip()
                for start in range(0, len(text), 750):
                    part = text[max(0, start-100):start+750].strip()
                    if part:
                        self.chunks.append({"file": path.name, "page": page, "text": part})
        if self.chunks:
            self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
            self.matrix = self.vectorizer.fit_transform([x["text"] for x in self.chunks])
        else:
            self.vectorizer = self.matrix = None
        return len(self.chunks)

    def retrieve(self, question, top_k=4):
        if self.matrix is None:
            return []
        q = self.vectorizer.transform([question])
        scores = cosine_similarity(q, self.matrix).ravel()
        ids = scores.argsort()[::-1][:top_k]
        return [{**self.chunks[i], "score": float(scores[i])} for i in ids if scores[i] > 0]

    def answer(self, question, top_k=4):
        sources = self.retrieve(question, top_k)
        if not sources:
            return "No relevant passage found. Add trusted PDF/TXT documents and re-index.", "retrieval-only", []
        context = "\n\n".join(f"[{i+1}] {s['file']} page {s['page']}: {s['text']}" for i, s in enumerate(sources))
        if LLM_BASE_URL and LLM_MODEL:
            try:
                headers = {"Content-Type": "application/json"}
                if LLM_API_KEY:
                    headers["Authorization"] = f"Bearer {LLM_API_KEY}"
                res = requests.post(LLM_BASE_URL.rstrip("/") + "/chat/completions",
                    headers=headers, json={"model": LLM_MODEL, "temperature": 0.2,
                    "messages": [
                        {"role": "system", "content": "Answer only from the supplied context. State when context is insufficient. This is educational information, not medical advice. Cite source numbers."},
                        {"role": "user", "content": f"Question: {question}\nContext:\n{context}"}]}, timeout=45)
                res.raise_for_status()
                return res.json()["choices"][0]["message"]["content"], "llm+retrieval", sources
            except Exception:
                pass
        return "LLM not configured; showing retrieved passages.\n\n" + "\n\n".join(f"[{i+1}] {s['text']}" for i, s in enumerate(sources)), "retrieval-only", sources

engine = RAGEngine()
