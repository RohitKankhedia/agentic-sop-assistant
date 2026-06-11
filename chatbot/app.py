"""
app.py
------
Streamlit web interface for the SOP Intelligence Chatbot.

Usage:
    streamlit run chatbot/app.py
"""

import os
import streamlit as st
from groq import Groq

# ── Config ─────────────────────────────────────────────────────────────
SOP_FILE  = os.path.join("data", "SOP_extracted.txt")
MODEL     = "llama-3.3-70b-versatile"
MAX_TOKENS = 1024

# ── Page setup ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SOP Assistant – Bank Rate Change",
    page_icon="🏦",
    layout="centered"
)

st.title("🏦 SOP Intelligence Assistant")
st.caption("Bank Rate Change Process · Indirect Auto | Direct Auto | Business Banking")
st.divider()

# ── Load SOP (cached so it only reads once) ────────────────────────────
@st.cache_resource
def load_sop():
    if not os.path.exists(SOP_FILE):
        st.error(f"SOP file not found at '{SOP_FILE}'. Run read_sop.py first.")
        st.stop()
    with open(SOP_FILE, "r", encoding="utf-8") as f:
        return f.read()

@st.cache_resource
def get_client():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        st.error("GROQ_API_KEY not set. Set it before running: $env:GROQ_API_KEY='your-key'")
        st.stop()
    return Groq(api_key=api_key)

sop_text = load_sop()
client   = get_client()

SYSTEM_PROMPT = f"""You are an expert SOP Assistant for a bank's lending operations team.
Answer questions ONLY using the SOP document provided below.

Rules:
1. Only use information from the SOP. Do not use outside knowledge.
2. If the answer is not in the SOP, say: "This information is not covered in the SOP."
3. Be specific — mention step numbers, role names, contact emails, and timeframes when available.
4. Keep answers concise and practical.
5. If a product category is mentioned (Indirect Auto, Direct Auto, Business Banking), focus on that category.

--- SOP DOCUMENT START ---
{sop_text}
--- SOP DOCUMENT END ---
"""

# ── Session state (stores chat history across reruns) ──────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Sidebar ────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("📋 About")
    st.write("This assistant answers questions based strictly on the Bank Rate Change SOP.")
    st.divider()

    st.header("💡 Try asking...")
    sample_questions = [
        "What is the first step in the rate change process?",
        "Who approves rate changes?",
        "How do I notify dealers for Indirect Auto?",
        "What is the SLA for a regulatory rate change?",
        "What should I do if the core system is not updated?",
        "How are floating rate business loans handled?",
        "Who do I contact if a business client disputes a rate change?",
        "What compliance regulations apply to Direct Auto?",
    ]
    for q in sample_questions:
        if st.button(q, use_container_width=True):
            st.session_state.pending_question = q

    st.divider()
    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.caption(f"Model: {MODEL}")
    st.caption(f"SOP words loaded: {len(sop_text.split())}")

# ── Display chat history ───────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Handle sidebar button click ────────────────────────────────────────
if "pending_question" in st.session_state:
    prompt = st.session_state.pop("pending_question")
else:
    prompt = st.chat_input("Ask a question about the SOP...")

# ── Process new question ───────────────────────────────────────────────
if prompt:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Build message list for API call
    api_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    api_messages += [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ]

    # Get response from Groq
    with st.chat_message("assistant"):
        with st.spinner("Checking SOP..."):
            try:
                response = client.chat.completions.create(
                    model=MODEL,
                    messages=api_messages,
                    max_tokens=MAX_TOKENS,
                    temperature=0.1,
                )
                answer = response.choices[0].message.content
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error(f"Error: {e}")
