"""Simple slugify fallback if python-slugify not installed."""
import re
import unicodedata


def slugify(text: str, max_length: int = 200) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text.lower())
    text = re.sub(r"[-\s]+", "-", text).strip("-")
    return text[:max_length]
