"""
router.py
---------
Looks at the user's question and decides which specialist
agent should handle it.

Agents available:
  - guidance    : next steps, how-to, process questions
  - escalation  : who to contact, escalation paths, ownership
  - compliance  : regulations, legal requirements, audit
  - general     : anything else about the SOP
"""

from groq import Groq
import os

MODEL = "llama-3.3-70b-versatile"

ROUTER_PROMPT = """You are a routing assistant. Read the user's question and decide which specialist agent should answer it.

Choose exactly ONE of these agents:
- guidance    : questions about steps, process, what to do next, how to handle a situation, timelines, frequency
- escalation  : questions about who to contact, who is responsible, escalation paths, contacts, emails, phone numbers, ownership
- compliance  : questions about regulations, legal requirements, compliance rules, audit, ECOA, Reg Z, MLA, usury
- general     : any other SOP question that doesn't fit above

Reply with ONLY the agent name — nothing else. No explanation.
Example reply: guidance
"""

def route(question: str, client: Groq) -> str:
    """Returns the agent name that should handle this question."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": ROUTER_PROMPT},
            {"role": "user",   "content": question},
        ],
        max_tokens=10,
        temperature=0.0,
    )
    agent = response.choices[0].message.content.strip().lower()

    # Safety fallback — if model returns something unexpected
    valid = {"guidance", "escalation", "compliance", "general"}
    return agent if agent in valid else "general"
