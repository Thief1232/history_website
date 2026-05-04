import shutil
import sqlite3
import tempfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse


HOME = Path.home()


@dataclass(frozen=True)
class BrowserSpec:
    key: str
    label: str
    roots: tuple[Path, ...]
    history_file: str
    query: str


FIREFOX_QUERY = """
    SELECT url, COALESCE(visit_count, 1)
    FROM moz_places
    WHERE hidden = 0 AND url IS NOT NULL
"""
CHROMIUM_QUERY = """
    SELECT url, COALESCE(visit_count, 1)
    FROM urls
    WHERE hidden = 0 AND url IS NOT NULL
"""


BROWSERS = {
    "firefox": BrowserSpec(
        key="firefox",
        label="Firefox",
        roots=(HOME / ".config" / "mozilla" / "firefox",),
        history_file="places.sqlite",
        query=FIREFOX_QUERY,
    ),
    "chrome": BrowserSpec(
        key="chrome",
        label="Google Chrome",
        roots=(HOME / ".config" / "google-chrome",),
        history_file="History",
        query=CHROMIUM_QUERY,
    ),
    "chromium": BrowserSpec(
        key="chromium",
        label="Chromium",
        roots=(HOME / ".config" / "chromium",),
        history_file="History",
        query=CHROMIUM_QUERY,
    ),
    "brave": BrowserSpec(
        key="brave",
        label="Brave",
        roots=(HOME / ".config" / "BraveSoftware" / "Brave-Browser",),
        history_file="History",
        query=CHROMIUM_QUERY,
    ),
    "edge": BrowserSpec(
        key="edge",
        label="Microsoft Edge",
        roots=(HOME / ".config" / "microsoft-edge",),
        history_file="History",
        query=CHROMIUM_QUERY,
    ),
    "opera": BrowserSpec(
        key="opera",
        label="Opera",
        roots=(HOME / ".config" / "opera",),
        history_file="History",
        query=CHROMIUM_QUERY,
    ),
    "vivaldi": BrowserSpec(
        key="vivaldi",
        label="Vivaldi",
        roots=(HOME / ".config" / "vivaldi",),
        history_file="History",
        query=CHROMIUM_QUERY,
    ),
}
BROWSER_LABELS = {key: browser.label for key, browser in BROWSERS.items()}


def available_browsers() -> dict[str, str]:
    return {
        key: spec.label
        for key, spec in BROWSERS.items()
        if find_history_file(spec, required=False) is not None
    }


def normalize_browser(browser: str) -> str:
    if browser in BROWSERS:
        return browser
    return "firefox"


def get_history_counts(browser: str) -> Counter[str]:
    browser = normalize_browser(browser)
    spec = BROWSERS[browser]
    source_db = find_history_file(spec)
    temp_db = copy_history_to_temp(source_db, browser)
    try:
        return count_domains(fetch_url_visits(temp_db, spec.query))
    finally:
        shutil.rmtree(temp_db.parent, ignore_errors=True)


def find_history_file(spec: BrowserSpec, required: bool = True) -> Path | None:
    candidates: list[Path] = []

    for root in spec.roots:
        if not root.exists():
            continue

        direct_history = root / spec.history_file
        if direct_history.exists():
            candidates.append(direct_history)

        candidates.extend(sorted(root.glob(f"*/{spec.history_file}")))

    if candidates:
        return candidates[0]

    if not required:
        return None

    roots = ", ".join(str(root) for root in spec.roots)
    raise FileNotFoundError(f"Не удалось найти файл истории {spec.label} в: {roots}")


def copy_history_to_temp(src: Path, browser: str) -> Path:
    temp_dir = Path(tempfile.mkdtemp(prefix=f"{browser}-history-"))
    dst = temp_dir / src.name
    shutil.copy2(src, dst)
    return dst


def fetch_url_visits(history_db: Path, query: str) -> list[tuple[str, int]]:
    with sqlite3.connect(history_db) as connection:
        rows = connection.execute(query).fetchall()
    return [(row[0], max(int(row[1] or 1), 1)) for row in rows]


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


def count_domains(url_visits: list[tuple[str, int]]) -> Counter[str]:
    counter: Counter[str] = Counter()
    for url, visits in url_visits:
        domain = extract_domain(url)
        if domain:
            counter[domain] += visits
    return counter
