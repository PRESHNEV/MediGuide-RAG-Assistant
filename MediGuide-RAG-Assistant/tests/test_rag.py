def test_rag_retrieval(tmp_path, monkeypatch):
    import app.rag as module
    monkeypatch.setattr(module, "KNOWLEDGE_DIR", tmp_path)
    (tmp_path / "demo.txt").write_text("Hydration means getting enough fluids.", encoding="utf-8")
    e = module.RAGEngine()
    assert e.ingest() > 0
    assert e.retrieve("hydration fluids")
