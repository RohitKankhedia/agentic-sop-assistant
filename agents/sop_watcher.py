"""
sop_watcher.py
--------------
Watches the SOP Word document for changes.
If the file is updated, it automatically re-extracts the text
so the chatbot always uses the latest SOP content.
"""

import os
import time

SOP_DOCX = os.path.join("data", "SOP_Bank_Rate_Change_Process.docx")
SOP_TXT  = os.path.join("data", "SOP_extracted.txt")


def get_last_modified(filepath: str) -> float:
    """Returns the file's last modified timestamp."""
    if os.path.exists(filepath):
        return os.path.getmtime(filepath)
    return 0.0


def extract_sop(docx_path: str, txt_path: str):
    """Re-runs the text extraction from the Word doc."""
    from docx import Document

    doc = Document(docx_path)
    lines = []

    for block in doc.element.body:
        tag = block.tag.split("}")[-1]
        if tag == "p":
            from docx.oxml.ns import qn
            text = "".join(
                node.text or ""
                for node in block.iter()
                if node.tag == qn("w:t")
            )
            if text.strip():
                lines.append(text.strip())
        elif tag == "tbl":
            from docx.table import Table
            tbl = Table(block, doc)
            for row in tbl.rows:
                row_cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_cells:
                    lines.append(" | ".join(row_cells))
            lines.append("")

    text = "\n".join(lines)
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(text)
    return text


def check_and_reload(last_modified_time: float) -> tuple[float, str | None]:
    """
    Checks if the SOP Word doc has changed since last_modified_time.
    If yes: re-extracts and returns (new_timestamp, new_text).
    If no:  returns (same_timestamp, None).
    """
    current_modified = get_last_modified(SOP_DOCX)

    if current_modified > last_modified_time:
        print(f"[SOP Watcher] Change detected! Re-extracting SOP...")
        new_text = extract_sop(SOP_DOCX, SOP_TXT)
        print(f"[SOP Watcher] Reloaded — {len(new_text.split())} words.")
        return current_modified, new_text

    return last_modified_time, None


def load_sop_text() -> tuple[str, float]:
    """
    Loads the current SOP text and returns (text, last_modified_timestamp).
    Regenerates SOP_TXT from the docx if it doesn't exist or is older.
    """
    docx_mod = get_last_modified(SOP_DOCX)
    txt_mod  = get_last_modified(SOP_TXT)

    if not os.path.exists(SOP_TXT) or docx_mod > txt_mod:
        text = extract_sop(SOP_DOCX, SOP_TXT)
    else:
        with open(SOP_TXT, "r", encoding="utf-8") as f:
            text = f.read()

    return text, docx_mod
