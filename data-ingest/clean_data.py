# data_ingest/clean_data.py
from typing import List, Dict, Any, Optional
import re
from bs4 import BeautifulSoup
from dateutil import parser as dtparser
try:
    from .utils import DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP, LOG
except ImportError:
    # Fallback for standalone execution
    from utils import DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP, LOG


def normalize_text(text: str) -> str:
    text = text or ""
    text = re.sub(r"[\r\t\u00A0]+", " ", text)
    text = re.sub(r" +", " ", text)
    return text.strip()


def clean_html_text(html: str) -> str:
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text(separator=" ")
    return normalize_text(text)


def parse_date_safe(date_str: Optional[str]) -> Optional[str]:
    if not date_str:
        return None
    try:
        dt = dtparser.parse(date_str)
        return dt.isoformat()
    except Exception:
        return None


def chunk_text(text: str, chunk_size: int = DEFAULT_CHUNK_SIZE, overlap: int = DEFAULT_CHUNK_OVERLAP) -> List[str]:
    text = normalize_text(text)
    if not text:
        return []
    chunks: List[str] = []
    start = 0
    length = len(text)
    while start < length:
        end = min(start + chunk_size, length)
        chunk = text[start:end]
        chunks.append(chunk)
        if end == length:
            break
        start = end - overlap
    return chunks


def prepare_article_for_embeddings(article: Dict[str, Any], chunk_size: int = DEFAULT_CHUNK_SIZE, overlap: int = DEFAULT_CHUNK_OVERLAP) -> List[Dict[str, Any]]:
    content = article.get("content") or article.get("summary") or article.get("title") or ""
    content = clean_html_text(content)
    chunks = chunk_text(content, chunk_size=chunk_size, overlap=overlap)
    docs = []
    for i, chunk in enumerate(chunks):
        docs.append(
            {
                "id": f"{article.get('id')}_chunk_{i}",
                "text": chunk,
                "meta": {
                    "source": article.get("source"),
                    "title": article.get("title"),
                    "link": article.get("link"),
                    "published": parse_date_safe(article.get("published")),
                    "chunk_index": i,
                },
            }
        )
    return docs
