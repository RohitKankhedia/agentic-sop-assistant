"""
app.py  (v3 — Multi-Agent + Confidence + Multi-SOP + Email)
------------------------------------------------------------
New in v3:
  1. Source citation shown below every answer
  2. Confidence score (1-10) with colour badge
  3. Multi-SOP support — loads all .docx files from data/
  4. Clarifying questions when query is ambiguous
  5. Email drafting agent

Usage:
    streamlit run chatbot/app.py
"""

import os
import sys
import streamlit as st
from groq import Groq

sys.path.append(os.path.abspath("."))

from agents import router, guidance_agent, escalation_agent, compliance_agent
from agents import confidence_agent, email_agent, multi_sop_agent
from agents.sop_watcher import load_sop_text, check_and_reload

# ── Config ─────────────────────────────────────────────────────────────
MODEL = "llama-3.3-70b-versatile"

AGENT_INFO = {
    "guidance":   {"label": "📋 Task Guidance Agent",          "color": "#1f77b4"},
    "escalation": {"label": "📞 Escalation & Ownership Agent", "color": "#d62728"},
    "compliance": {"label": "⚖️ Compliance Agent",             "color": "#2ca02c"},
    "email":      {"label": "✉️ Email Drafting Agent",          "color": "#9467bd"},
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
        st.error("GROQ_API_KEY not set.")
        st.stop()
    return Groq(api_key=api_key)

client = get_client()

# ── Load all SOPs from data/ ───────────────────────────────────────────
@st.cache_resource
def get_all_sops():
    return multi_sop_agent.load_all_sops()

all_sops = get_all_sops()

# ── Primary SOP (for single-SOP agents) with auto-refresh ─────────────
if "sop_text" not in st.session_state or "sop_last_modified" not in st.session_state:
    sop_text, last_mod = load_sop_text()
    st.session_state.sop_text          = sop_text
    st.session_state.sop_last_modified = last_mod
else:
    new_mod, new_text = check_and_reload(st.session_state.sop_last_modified)
    if new_text:
        st.session_state.sop_text          = new_text
        st.session_state.sop_last_modified = new_mod
        st.cache_resource.clear()   # reload all_sops too
        st.toast("📄 SOP updated and reloaded!", icon="🔄")

sop_text = st.session_state.sop_text

if "messages" not in st.session_state:
    st.session_state.messages = []

# ══ SIDEBAR ════════════════════════════════════════════════════════════
with st.sidebar:
    st.title("🏦 SOP Assistant")
    st.caption("Bank Rate Change Process")
    st.divider()

    # User email (for email drafting agent)
    user_email = st.text_input(
        "📧 Your email address",
        value="",
        placeholder="you@bank.com",
        help="Used by the Email Drafting Agent to fill in the sender details"
    )

    st.divider()

    category = st.selectbox(
        "📂 Product Category",
        ["All Categories", "Indirect Auto", "Direct Auto", "Business Banking"],
    )

    st.divider()

    # SOP documents loaded
    st.subheader("📄 SOPs Loaded")
    if all_sops:
        for fname in all_sops:
            sop_path = os.path.abspath(os.path.join("data", fname))
            st.markdown(f"✅ {fname}")
    else:
        st.warning("No SOP files found in data/")

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
        "✉️ Email": [
            "Write an email to notify a dealer about the rate update",
            "Draft an escalation email to the IT team about a core system issue",
            "Write a notice email to a business client about rate change",
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

    st.caption(f"Primary SOP: {len(sop_text.split())} words loaded")


# ── Helper: confidence badge ───────────────────────────────────────────
def confidence_badge(score: int, reasoning: str) -> str:
    if score >= 8:
        color, label = "#2ca02c", "High"
    elif score >= 5:
        color, label = "#ff7f0e", "Medium"
    else:
        color, label = "#d62728", "Low"

    return (
        f"<div style='margin-top:8px; padding:6px 10px; background:#f0f2f6; "
        f"border-radius:6px; font-size:0.8em;'>"
        f"<b>Confidence:</b> "
        f"<span style='color:{color}; font-weight:bold;'>{label} ({score}/10)</span> "
        f"— {reasoning}"
        f"</div>"
    )


# ── Helper: source citation ────────────────────────────────────────────
def source_citation(sop_filename: str) -> str:
    sop_path = os.path.abspath(os.path.join("data", sop_filename))
    return (
        f"<div style='margin-top:6px; font-size:0.78em; color:#666;'>"
        f"📄 <b>Source:</b> {sop_filename} &nbsp;|&nbsp; "
        f"<span title='{sop_path}' style='cursor:help; text-decoration:underline dotted;'>"
        f"📂 {sop_path}</span>"
        f"</div>"
    )


# ══ MAIN AREA ══════════════════════════════════════════════════════════
st.title("🏦 Agentic SOP Intelligence Assistant")
st.caption("Answers sourced only from SOP documents · Multi-Agent AI · v3")
st.divider()

# ── Chat input ─────────────────────────────────────────────────────────
if "pending_question" in st.session_state:
    prompt = st.session_state.pop("pending_question")
else:
    prompt = st.chat_input("Ask anything about the Bank Rate Change SOP...")

# ── Process new question ───────────────────────────────────────────────
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Route first — email requests must NEVER hit clarification
    agent_name = router.route(prompt, client)

    history = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages[:-1]
    ]

    # Only check clarification for non-email, non-specific agents
    needs_clarify, clarify_q = False, ""
    if agent_name == "general":
        needs_clarify, clarify_q = multi_sop_agent.needs_clarification(prompt, client)

    if needs_clarify:
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"🤔 {clarify_q}",
            "agent": "general",
            "is_clarification": True,
            "sop_used": "",
            "confidence": None,
        })
    else:
        try:
            sop_used = list(all_sops.keys())[0] if all_sops else "SOP_Bank_Rate_Change_Process.docx"

            if agent_name == "email":
                email_addr = user_email or "staff@bank.com"
                # Use the best SOP for email context
                _, sop_used = multi_sop_agent.ask(prompt, [], all_sops, client, category)
                email_sop   = all_sops.get(sop_used, sop_text)
                answer = email_agent.ask(prompt, history, email_sop, client, email_addr)
                conf   = None

            elif agent_name == "guidance":
                answer, sop_used = multi_sop_agent.ask(prompt, history, all_sops, client, category)
                conf   = confidence_agent.score(prompt, answer, client)

            elif agent_name == "escalation":
                answer, sop_used = multi_sop_agent.ask(prompt, history, all_sops, client, category)
                conf   = confidence_agent.score(prompt, answer, client)

            elif agent_name == "compliance":
                answer, sop_used = multi_sop_agent.ask(prompt, history, all_sops, client, category)
                conf   = confidence_agent.score(prompt, answer, client)

            else:
                # General — use multi-SOP agent
                answer, sop_used = multi_sop_agent.ask(prompt, history, all_sops, client, category)
                conf = confidence_agent.score(prompt, answer, client)

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "agent": agent_name,
                "is_clarification": False,
                "sop_used": sop_used,
                "confidence": conf,
            })

        except Exception as e:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"❌ Error: {e}",
                "agent": "general",
                "is_clarification": False,
                "sop_used": "",
                "confidence": None,
            })

# ── Render full chat history ───────────────────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])
    else:
        with st.chat_message("assistant"):
            agent_name = msg.get("agent", "general")
            info       = AGENT_INFO.get(agent_name, AGENT_INFO["general"])

            # Agent label
            if not msg.get("is_clarification"):
                st.markdown(
                    f"<small style='color:{info['color']}'>{info['label']}</small>",
                    unsafe_allow_html=True
                )

            # Answer
            st.markdown(msg["content"])

            # Source citation
            sop_used = msg.get("sop_used", "")
            if sop_used and not msg.get("is_clarification"):
                st.markdown(source_citation(sop_used), unsafe_allow_html=True)

            # Confidence badge
            conf = msg.get("confidence")
            if conf and not msg.get("is_clarification"):
                st.markdown(
                    confidence_badge(conf["score"], conf["reasoning"]),
                    unsafe_allow_html=True
                )
