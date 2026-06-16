"""
multi_sop_agent.py
------------------
Loads ALL SOP documents from the data/ folder.
Identifies which SOP is most relevant to the question.
Only asks a clarifying question if the query is extremely vague (< 5 words, no clear intent).
"""

import os
from docx import Document
from docx.oxml.ns import qn
from docx.table import Table

MODEL    = "llama-3.3-70b-versatile"
DATA_DIR = "data"


# ── Load all SOPs from data/ ───────────────────────────────────────────
def load_all_sops() -> dict:
    sops = {}
    if not os.path.exists(DATA_DIR):
        return sops
    for fname in os.listdir(DATA_DIR):
        if fname.endswith(".docx"):
            path = os.path.join(DATA_DIR, fname)
            try:
                sops[fname] = _extract(path)
            except Exception as e:
                print(f"[MultiSOP] Could not load {fname}: {e}")
    return sops


def _extract(filepath: str) -> str:
    doc   = Document(filepath)
    lines = []
    for block in doc.element.body:
        tag = block.tag.split("}")[-1]
        if tag == "p":
            text = "".join(
                node.text or ""
                for node in block.iter()
                if node.tag == qn("w:t")
            )
            if text.strip():
                lines.append(text.strip())
        elif tag == "tbl":
            tbl = Table(block, doc)
            for row in tbl.rows:
                cells = [c.text.strip() for c in row.cells if c.text.strip()]
                if cells:
                    lines.append(" | ".join(cells))
            lines.append("")
    return "\n".join(lines)


# ── Pick the most relevant SOP ─────────────────────────────────────────
def pick_sop(question: str, sop_names: list, client) -> str:
    if len(sop_names) == 1:
        return sop_names[0]

    names_list = "\n".join(f"- {n}" for n in sop_names)
    prompt = f"""You are a document router. Given a user question and a list of SOP filenames, pick the ONE most relevant document.
Reply with ONLY the exact filename — nothing else.

SOPs available:
{names_list}

Question: {question}
"""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=60,
        temperature=0.0,
    )
    chosen = response.choices[0].message.content.strip()
    return chosen if chosen in sop_names else sop_names[0]


# ── Check if question needs clarification ─────────────────────────────
def needs_clarification(question: str, client) -> tuple[bool, str]:
    """
    Only asks for clarification when the question is very short AND has no clear intent.
    Long questions or questions with clear action words are NEVER flagged.
    """
    words = question.strip().split()

    # Never ask for clarification if question is 5+ words — it has enough context
    if len(words) >= 5:
        return False, ""

    # For very short queries, check if there's a clear keyword that makes intent obvious
    clear_keywords = [
        "email", "escalat", "rate", "loan", "wire", "ach", "kyc", "aml", "sar", "ctr",
        "eod", "batch", "step", "process", "contact", "who", "what", "how", "when",
        "approve", "compli", "regul", "ofac", "underwr", "disburse", "close"
    ]
    q_lower = question.lower()
    if any(kw in q_lower for kw in clear_keywords):
        return False, ""

    # Only ask for clarification on truly ambiguous short queries (e.g. "number", "help", "yes")
    prompt = """A user asked a very short question to a banking SOP chatbot.
Is it too vague to answer without clarification?

Reply CLARIFY: <one short question> if truly ambiguous.
Reply CLEAR if there is enough context to attempt an answer.

Rules:
- If the question has any banking or process keyword, reply CLEAR.
- Only reply CLARIFY for completely meaningless queries like single words with no context.
"""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user",   "content": question},
        ],
        max_tokens=60,
        temperature=0.0,
    )
    reply = response.choices[0].message.content.strip()
    if reply.startswith("CLARIFY:"):
        return True, reply[len("CLARIFY:"):].strip()
    return False, ""


# ── Answer using the best SOP ─────────────────────────────────────────
def ask(question: str, history: list, sops: dict, client, category_filter: str = "All Categories") -> tuple[str, str]:
    if not sops:
        return "No SOP documents found in the data/ folder.", ""

    sop_names  = list(sops.keys())
    chosen_sop = pick_sop(question, sop_names, client)
    sop_text   = sops[chosen_sop]

    category_note = f"Focus on: {category_filter}." if category_filter != "All Categories" else ""

    system = f"""You are an expert SOP assistant for a bank's operations team.
Answer ONLY from the SOP document below. {category_note}
Reference specific section names and step numbers when available.
If the answer is not in the SOP, say so clearly — do not guess.

--- SOP: {chosen_sop} ---
{sop_text}
--- END ---
"""
    messages = [{"role": "system", "content": system}]
    messages += history
    messages.append({"role": "user", "content": question})

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_tokens=1024,
        temperature=0.1,
    )
    return response.choices[0].message.content, chosen_sop
