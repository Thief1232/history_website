from collections import Counter
from typing import TypedDict


class ChartItem(TypedDict):
    domain: str
    visits: int


class ChartRow(ChartItem):
    width: float


def build_chart_data(domain_counts: Counter[str], limit: int) -> list[ChartItem]:
    most_common = domain_counts.most_common()
    common = most_common[:limit]
    others = most_common[limit:]

    chart_data: list[ChartItem] = [
        {"domain": domain, "visits": visits} for domain, visits in common
    ]
    other_visits = sum(count for _, count in others)
    if other_visits:
        chart_data.append({"domain": f"Others ({len(others)})", "visits": other_visits})

    return chart_data


def build_chart_rows(chart_data: list[ChartItem]) -> list[ChartRow]:
    max_visits = max((item["visits"] for item in chart_data), default=0)
    rows: list[ChartRow] = []

    for item in chart_data:
        width = 0 if max_visits == 0 else max(4, item["visits"] / max_visits * 100)
        rows.append({**item, "width": width})

    return rows
