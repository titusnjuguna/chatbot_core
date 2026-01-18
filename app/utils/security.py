import re
from pathlib import Path

def sanitize_filename(filename: str) -> str:
    """Prevent path traversal and invalid names"""
    # Remove dangerous characters
    safe = re.sub(r"[^a-zA-Z0-9._-]", "_", filename)
    # Ensure it ends with .pdf
    if not safe.lower().endswith(".pdf"):
        safe += ".pdf"
    # Prevent hidden files
    if safe.startswith("."):
        safe = "file" + safe
    # Resolve to prevent ../ attacks
    resolved = Path(safe).resolve()
    if resolved.name != safe:
        raise ValueError("Invalid filename")
    return resolved.name