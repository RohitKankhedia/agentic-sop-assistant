"""
app.py  (v2 — Multi-Agent)
--------------------------
Streamlit web interface for the Agentic SOP Intelligence Assistant.
Routes each question to the right specialist agent automatically.

Usage:
    streamlit run chatbot/app.py
"""

import os
import sys
import streamlit as st
from groq import Groq

sys.path.append(os.path.abspath("."))

from agents import router, guidance_agent, escalation_agent, compliance_agent
from agents.sop_watcher import load_sop_text, check_and_reload

# ── Config ─────────────────────────────────────────────────────────────
MODEL = "llama-3.3-70b-versatile"

AGENT_INFO = {
    "guidance":   {"label": "📋 Task Guidance Agent",          "color": "#1f77b4"},
    "escalation": {"label": "📞 Escalation & Ownership Agent", "color": "#d62728"},
    "compliance": {"label": "⚖️ Compliance Agent",             "color": "#2ca02c"},
    "general":    {"label": "🤖 SOP General Agent",            "color": "#7f7f7f"},
}

# ── Page setup ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SOP Intelligence Assistant",
    page_icon="🏦",
    layout="wide"
)

# ── Groq client ────────────────────────────────────────────────────────
@st.cache_resource
def get_client():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        st.error("GROQ_API_KEY not set. Run: $env:GROQ_API_KEY='your-key'")
        st.stop()
    return Groq(api_key=api_key)

client = get_client()

# ── SOP loading with auto-refresh ──────────────────────────────────────
if "sop_text" not in st.session_state or "sop_last_modified" not in st.session_state:
    sop_text, last_mod = load_sop_text()
    st.session_state.sop_text          = sop_text
    st.session_state.sop_last_modified = last_mod
else:
    new_mod, new_text = check_and_reload(st.session_state.sop_last_modified)
    if new_text:
        st.session_state.sop_text          = new_text
        st.session_state.sop_last_modified = new_mod
        st.toast("📄 SOP document updated and reloaded!", icon="🔄")

sop_text = st.session_state.sop_text

if "messages" not in st.session_state:
    st.session_state.messages = []

# ══ SIDEBAR ════════════════════════════════════════════════════════════
with st.sidebar:
    st.title("🏦 SOP Assistant")
    st.caption("Bank Rate Change Process")
    st.divider()

    category = st.selectbox(
        "📂 Product Category",
        ["All Categories", "Indirect Auto", "Direct Auto", "Business Banking"],
    )

    st.divider()
    st.subheader("🤖 Active Agents")
    for info in AGENT_INFO.values():
        st.markdown(
            f"<span style='color:{info['color']}'>●</span> {info['label']}",
            unsafe_allow_html=True
        )

    st.divider()
    st.subheader("💡 Sample Questions")

    samples = {
        "📋 Process": [
            "What is the first step in the rate change process?",
            "How do I handle a floating rate business loan change?",
            "What happens after ALCO approves a rate change?",
        ],
        "📞 Escalation": [
            "Who approves rate changes?",
            "What should I do if the core system is not updated on time?",
            "Who do I contact if a dealer didn't get the rate sheet?",
        ],
        "⚖️ Compliance": [
            "What compliance regulations apply to Direct Auto?",
            "What is the MLA rate cap for auto loans?",
            "How long must rate change documents be retained?",
        ],
    }

    for group, questions in samples.items():
        with st.expander(group):
            for q in questions:
                if st.button(q, key=q, use_container_width=True):
                    st.session_state.pending_question = q

    st.divider()
    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.caption(f"SOP words loaded: {len(sop_text.split())}")

# ══ MAIN AREA ══════════════════════════════════════════════════════════
st.title("🏦 Agentic SOP Intelligence Assistant")
st.caption("Answers sourced only from the Bank Rate Change SOP · Multi-Agent AI")
st.divider()

# ── Chat input (OUTSIDE columns — sticks to page bottom correctly) ─────
if "pending_question" in st.session_state:
    prompt = st.session_state.pop("pending_question")
else:
    prompt = st.chat_input("Ask anything about the Bank Rate Change SOP...")

# ── Process new question BEFORE rendering history ──────────────────────
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Route to correct agent
    agent_name = router.route(prompt, client)
    info       = AGENT_INFO.get(agent_name, AGENT_INFO["general"])

    history = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages[:-1]
    ]

    try:
        if agent_name == "guidance":
            answer = guidance_agent.ask(prompt, history, sop_text, client, category)
        elif agent_name == "escalation":
            answer = escalation_agent.ask(prompt, history, sop_text, client, category)
        elif agent_name == "compliance":
            answer = compliance_agent.ask(prompt, history, sop_text, client, category)
        else:
            answer = guidance_agent.ask(prompt, history, sop_text, client, category)

        full_answer = f"<small style='color:{info['color']}'>{info['label']}</small>\n\n{answer}"
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "agent": agent_name,
        })
    except Exception as e:
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"❌ Error: {e}",
            "agent": "general",
        })

# ── Render full chat history (messages appear above input box) ─────────
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])
    else:
        with st.chat_message("assistant"):
            agent_name = msg.get("agent", "general")
            info       = AGENT_INFO.get(agent_name, AGENT_INFO["general"])
            st.markdown(
                f"<small style='color:{info['color']}'>{info['label']}</small>",
                unsafe_allow_html=True
            )
            st.markdown(msg["content"])
