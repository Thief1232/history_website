import shutil
import sqlite3
import tempfile
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

from config import FIREFOX_ROOT


def find_firefox_history_file() -> Path:
    if not FIREFOX_ROOT.exists():
        raise FileNotFoundError(f"Firefox config directory not found: {FIREFOX_ROOT}")

    candidates = sorted(FIREFOX_ROOT.glob("*.default*/places.sqlite"))
    if not candidates:
        candidates = sorted(FIREFOX_ROOT.glob("*/places.sqlite"))

    if not candidates:
        raise FileNotFoundError("Could not find Firefox history file places.sqlite")

    return candidates[0]


def copy_history_to_temp(src: Path) -> Path:
    temp_dir = Path(tempfile.mkdtemp(prefix="firefox-history-"))
    dst = temp_dir / src.name
    shutil.copy2(src, dst)
    return dst


def fetch_urls(history_db: Path) -> list[str]:
    query = """
        SELECT url
        FROM moz_places
        WHERE hidden = 0 AND url IS NOT NULL
    """
    with sqlite3.connect(history_db) as connection:
        rows = connection.execute(query).fetchall()
    return [row[0] for row in rows]


def extract_domain(url: str) -> str | None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return None

    domain = parsed.netloc.lower()
    if domain.startswith("www."):
        domain = domain[4:]

    parts = domain.split(".")
    if len(parts) >= 2:
        domain = ".".join(parts[-2:])

    return domain or None


def count_domains(urls: list[str]) -> Counter[str]:
    counter: Counter[str] = Counter()
    for url in urls:
        domain = extract_domain(url)
        if domain:
            counter[domain] += 1
    return counter


def get_history_counts() -> Counter[str]:
    source_db = find_firefox_history_file()
    temp_db = copy_history_to_temp(source_db)
    try:
        return count_domains(fetch_urls(temp_db))
    finally:
        shutil.rmtree(temp_db.parent, ignore_errors=True)
