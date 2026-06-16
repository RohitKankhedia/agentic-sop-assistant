"""
confidence_agent.py
-------------------
Backend agent that rates how confident the answer is
based on how well the SOP covers the question.
Returns a score 1-10 and a short reasoning note.
"""

import json
MODEL = "llama-3.3-70b-versatile"

PROMPT = """You are a quality checker for an SOP-based AI assistant.

Given a user question and the assistant's answer, rate how confident
you are that the answer is accurate and fully sourced from the SOP.

Return ONLY valid JSON in this exact format (no extra text):
{
  "score": <integer 1 to 10>,
  "reasoning": "<one short sentence explaining the score>"
}

Scoring guide:
10 — Answer is directly and completely found in the SOP
8-9 — Answer is mostly in the SOP with minor inference
6-7 — Answer is partially in the SOP; some gaps
4-5 — Answer is loosely related to SOP content
1-3 — Answer could not be properly sourced from the SOP
"""

def score(question: str, answer: str, client) -> dict:
    """Returns {"score": int, "reasoning": str}"""
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": PROMPT},
                {"role": "user",   "content": f"QUESTION: {question}\n\nANSWER: {answer}"},
            ],
            max_tokens=100,
            temperature=0.0,
        )
        raw = response.choices[0].message.content.strip()
        return json.loads(raw)
    except Exception:
        return {"score": 7, "reasoning": "Confidence check unavailable."}
