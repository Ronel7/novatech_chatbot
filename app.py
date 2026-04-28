import os
import re
import streamlit as st

# Désactivation des logs superflus
os.environ["TRANSFORMERS_VERBOSITY"] = "error"

# ─── Configuration de la Page ────────────────────────────────────────────────
st.set_page_config(
    page_title="NovaTech RH Assistant",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Design CSS (NovaTech Navy & White) ──────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
html { scroll-behavior: smooth; }
.stApp { background: #F7F8FA; }

[data-testid="stSidebar"] { background: #0F2447; border-right: 1px solid #1A3A6E; }
[data-testid="stSidebar"] * { color: #C8D8F0 !important; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #FFFFFF !important; }

.nt-header {
    background: linear-gradient(135deg, #0F2447 0%, #1A3C6E 60%, #1E5799 100%);
    border-radius: 16px; padding: 28px 36px; margin-bottom: 24px;
    display: flex; align-items: center; gap: 20px;
}
.nt-header-title { color: #FFFFFF; font-size: 1.6rem; font-weight: 600; margin: 0; }
.nt-header-sub   { color: #7BACD4; font-size: 0.85rem; margin: 2px 0 0 0; }

.msg-user {
    background: #1A3C6E; color: #FFFFFF;
    border-radius: 18px 18px 4px 18px; padding: 14px 20px;
    margin: 10px 0 10px 15%; line-height: 1.55;
    box-shadow: 0 2px 12px rgba(15,36,71,0.15);
}
.msg-assistant {
    background: #FFFFFF; color: #1C2B3A;
    border-radius: 4px 18px 18px 18px; padding: 18px 22px;
    margin: 10px 15% 10px 0; line-height: 1.65;
    box-shadow: 0 2px 16px rgba(0,0,0,0.06); border: 1px solid #E8EDF4;
}

/* Citation inline cliquable */
.src-ref {
    display: inline-block; background: #E8EDF8; color: #1A3C6E !important;
    font-size: 0.72rem; font-weight: 700; padding: 1px 7px;
    border-radius: 6px; margin: 0 2px; font-family: 'DM Mono', monospace;
    border: 1px solid #C0D0E8; text-decoration: none !important;
    transition: all 0.2s; cursor: pointer;
}
.src-ref:hover { background: #1A3C6E; color: white !important; transform: translateY(-1px); }

/* Cartes sources */
.sources-wrap { margin: 12px 15% 4px 0; }
.sources-title {
    font-size: 0.72rem; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.8px; color: #7A8CA0; margin-bottom: 8px;
}
.source-card {
    display: flex; align-items: flex-start; gap: 10px;
    background: #FFFFFF; border: 1px solid #DCE8F5;
    border-left: 4px solid #1A3C6E; border-radius: 0 8px 8px 0;
    padding: 12px 15px; margin: 8px 0; font-size: 0.82rem;
    scroll-margin-top: 100px;
}
.src-num {
    min-width: 24px; height: 24px; border-radius: 50%;
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 0.75rem; font-weight: 700; font-family: 'DM Mono', monospace;
    background: #E8EDF8; color: #1A3C6E; flex-shrink: 0;
}
.src-body { flex: 1; }
.src-name  { font-weight: 600; color: #1A3C6E; }
.src-meta  { color: #7A8CA0; font-size: 0.75rem; margin-top: 2px; }
.src-excerpt { color: #4A607A; font-size: 0.78rem; font-style: italic; margin-top: 5px; line-height: 1.45; }

.sug-btn > button {
    background: #FFFFFF !important; color: #1A3C6E !important;
    border: 1px solid #C0D4EC !important; border-radius: 20px !important;
    font-size: 0.83rem !important; padding: 6px 14px !important;
}
</style>
""", unsafe_allow_html=True)

# ─── Helpers ─────────────────────────────────────────────────────────────────

ICONS = {"pdf": "📄", "docx": "📝", "xlsx": "📊", "png": "🖼️", "jpg": "🖼️", "json": "🔧", "md": "📋"}

def format_citations(text: str, msg_id: str = "") -> str:
    """Transforme [1], [2] en badges <a> cliquables avec ancres uniques par message."""
    text = re.sub(r'\[SOURCE_(\d+)\]', r'[\1]', text)
    def repl(m):
        nums = re.findall(r'\d+', m.group(0))
        return "".join([f'<a href="#source-{n}-{msg_id}" class="src-ref">{n}</a>' for n in nums])
    return re.sub(r'\[\s*\d+[\s,\d]*\]', repl, text)

def source_html(s: dict, show_excerpt: bool, msg_id: str = "") -> str:
    idx = s['index']
    icon = ICONS.get(s.get("source_type", ""), "📁")
    anchor = f"source-{idx}-{msg_id}"
    
    meta_parts = []
    if s.get("page"): meta_parts.append(f"Page {s['page']}")
    if s.get("section"): meta_parts.append(s["section"][:45])
    meta = " · ".join(meta_parts) or s.get("source_type", "").upper()

    excerpt_html = ""
    if show_excerpt and s.get("excerpt"):
        excerpt_html = f'<div class="src-excerpt">"{s["excerpt"]}"</div>'

    return f"""
<div id="{anchor}" class="source-card">
  <span class="src-num">{idx}</span>
  <div class="src-body">
    <div class="src-name">{icon} {s['source_file']}</div>
    <div class="src-meta">{meta}</div>
    {excerpt_html}
  </div>
</div>"""

# ─── Logic ──────────────────────────────────────────────────────────────────

if "messages" not in st.session_state: st.session_state.messages = []
if "rag_ready" not in st.session_state: st.session_state.rag_ready = False

@st.cache_resource(show_spinner=False)
def load_rag():
    from src.retriever import NovaTechRAG
    return NovaTechRAG()

# ─── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 💼 NovaTech RH")
    if not st.session_state.rag_ready:
        with st.spinner("Initialisation..."):
            st.session_state.rag = load_rag()
            st.session_state.stats = st.session_state.rag.get_collection_stats()
            st.session_state.rag_ready = True
    
    if st.session_state.rag_ready:
        s = st.session_state.stats
        c1, c2 = st.columns(2)
        c1.metric("Docs", s.get("total_documents", 0))
        c2.metric("Segments", s.get("total_chunks", 0))

    st.divider()
    show_sources  = st.toggle("Afficher les sources", value=True)
    show_excerpts = st.toggle("Afficher les extraits", value=False)
    
    if st.button("🗑️ Vider la conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ─── Header ───────────────────────────────────────────────────────────────────

st.markdown("""
<div class="nt-header">
  <div style="font-size:2.6rem">💼</div>
  <div>
    <p class="nt-header-title">Assistant RH — NovaTech SAS</p>
    <p class="nt-header-sub">Réponses précises basées sur les documents officiels</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── Suggestions ──────────────────────────────────────────────────────────────

if not st.session_state.messages:
    st.markdown("**Suggestions :**")
    suggestions = ["Comment demander des congés ?", "Politique de télétravail", "Avantages mutuelle"]
    cols = st.columns(len(suggestions))
    for i, sug in enumerate(suggestions):
        if cols[i].button(sug, key=f"sug_{i}", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": sug})
            st.rerun()

# ─── Affichage Historique ─────────────────────────────────────────────────────

for msg_idx, msg in enumerate(st.session_state.messages):
    mid = str(msg_idx)
    if msg["role"] == "user":
        st.markdown(f'<div class="msg-user">🧑 {msg["content"]}</div>', unsafe_allow_html=True)
    else:
        data = msg["content"]
        answer_html = format_citations(data["answer"], msg_id=mid)
        st.markdown(f'<div class="msg-assistant">{answer_html}</div>', unsafe_allow_html=True)
        if show_sources and data.get("sources"):
            cards = "".join(source_html(s, show_excerpts, msg_id=mid) for s in data["sources"])
            st.markdown(f'<div class="sources-wrap"><div class="sources-title">📎 Documents de référence</div>{cards}</div>', unsafe_allow_html=True)

# ─── Traitement ───────────────────────────────────────────────────────────────

st.markdown("<br>", unsafe_allow_html=True)

if st.session_state.rag_ready:
    # 1. Saisie Formulaire
    with st.form("chat_form", clear_on_submit=True):
        ci, cb = st.columns([5, 1])
        user_input = ci.text_input("Question", placeholder="Posez votre question RH…", label_visibility="collapsed")
        submitted = cb.form_submit_button("Envoyer ➤", use_container_width=True)

    if submitted and user_input.strip():
        st.session_state.messages.append({"role": "user", "content": user_input.strip()})
        st.rerun()

    # 2. Moteur de réponse (Gère suggestions + saisie)
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        query = st.session_state.messages[-1]["content"]
        new_mid = str(len(st.session_state.messages))
        
        # Zone d'affichage temporaire pour le "streaming"
        placeholder = st.empty()
        
        with st.spinner("🔍 Recherche..."):
            result = st.session_state.rag.ask(query)

        # Simulation Streaming
        streamed = ""
        words = result.answer.split(" ")
        for i, word in enumerate(words):
            streamed += word + " "
            if i % 6 == 0:
                placeholder.markdown(f'<div class="msg-assistant">{format_citations(streamed.rstrip(), msg_id=new_mid)}▌</div>', unsafe_allow_html=True)
        
        # Stockage final
        st.session_state.messages.append({
            "role": "assistant",
            "content": {
                "answer": result.answer,
                "sources": [s.__dict__ for s in result.sources]
            }
        })
        st.rerun()