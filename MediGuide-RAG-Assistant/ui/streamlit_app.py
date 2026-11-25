import streamlit as st
import requests
API = "http://127.0.0.1:8000"
st.set_page_config(page_title="MediGuide", page_icon="🩺")
st.title("🩺 MediGuide")
st.caption("Document-grounded health education demo. Not a diagnostic tool or medical advice.")
if st.button("Re-index PDF/TXT knowledge base"):
    try:
        r = requests.post(API + "/ingest", timeout=60); r.raise_for_status()
        st.success(f"Indexed {r.json()['chunks']} chunks")
    except requests.RequestException as e:
        st.error(str(e))
if "history" not in st.session_state: st.session_state.history = []
for m in st.session_state.history:
    with st.chat_message(m["role"]): st.markdown(m["content"])
q = st.chat_input("Ask about the indexed documents...")
if q:
    st.session_state.history.append({"role":"user","content":q})
    with st.chat_message("user"): st.write(q)
    with st.chat_message("assistant"):
        try:
            r = requests.post(API + "/ask", json={"question":q}, timeout=60); r.raise_for_status()
            d = r.json(); st.markdown(d["answer"]); st.caption("Mode: " + d["mode"])
            with st.expander("Sources"):
                for s in d["sources"]: st.write(f"{s['file']} · page {s['page'] or 'N/A'} · {s['score']:.3f}\n\n{s['text'][:600]}")
            st.session_state.history.append({"role":"assistant","content":d["answer"]})
        except requests.RequestException as e: st.error(f"Start the API first: {e}")
