from fastapi import FastAPI
from pydantic import BaseModel, Field
from app.rag import engine
app = FastAPI(title="MediGuide RAG API", description="Educational demo, not medical advice.")
class Ask(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    top_k: int = Field(default=4, ge=1, le=10)
@app.on_event("startup")
def startup():
    engine.ingest()
@app.get("/health")
def health():
    return {"status": "ok", "chunks": len(engine.chunks)}
@app.post("/ingest")
def ingest():
    return {"status": "indexed", "chunks": engine.ingest()}
@app.post("/ask")
def ask(req: Ask):
    answer, mode, sources = engine.answer(req.question, req.top_k)
    return {"answer": answer, "mode": mode, "sources": sources}
