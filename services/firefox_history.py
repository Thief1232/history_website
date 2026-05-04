from collections import Counter

from services.browser_history import count_domains as count_weighted_domains
from services.browser_history import extract_domain
from services.browser_history import get_history_counts as get_browser_history_counts


def count_firefox_domains(urls: list[str]) -> Counter[str]:
    return count_weighted_domains([(url, 1) for url in urls])


def count_domains(urls: list[str]) -> Counter[str]:
    return count_firefox_domains(urls)


def get_history_counts() -> Counter[str]:
    return get_browser_history_counts("firefox")
