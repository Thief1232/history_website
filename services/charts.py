from collections import Counter
from math import cos, radians, sin
from typing import Any, TypedDict


CHART_TYPES = ("bar", "pie")
CHART_LABELS = {
    "bar": "Bar",
    "pie": "Pie",
}
CHART_COLORS = ("#38bdf8", "#818cf8", "#f472b6", "#34d399", "#fbbf24", "#fb7185", "#a78bfa", "#22d3ee")


class ChartItem(TypedDict):
    domain: str
    visits: int


class ChartRow(ChartItem):
    width: float


def normalize_chart_type(chart_type: str) -> str:
    if chart_type in CHART_TYPES:
        return chart_type
    return "bar"


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


def build_chart_model(chart_data: list[ChartItem], chart_type: str) -> dict[str, Any]:
    return {
        "type": normalize_chart_type(chart_type),
        "rows": build_chart_rows(chart_data),
        "pie": build_pie_model(chart_data),
    }


def build_pie_model(chart_data: list[ChartItem]) -> dict[str, Any]:
    total = sum(item["visits"] for item in chart_data)
    current = 0.0
    gradient_parts = []
    slices = []

    for index, item in enumerate(chart_data):
        color = CHART_COLORS[index % len(CHART_COLORS)]
        percent = 0 if total == 0 else item["visits"] / total * 100
        next_value = current + percent
        angle = (current + percent / 2) * 3.6
        gradient_parts.append(f"{color} {current:.2f}% {next_value:.2f}%")
        slices.append(
            {
                **item,
                "color": color,
                "percent": percent,
                "show_label": percent >= 4,
                "label_x": 50 + sin(radians(angle)) * 30,
                "label_y": 50 - cos(radians(angle)) * 30,
            }
        )
        current = next_value

    return {
        "style": f"background: conic-gradient({', '.join(gradient_parts)});" if gradient_parts else "",
        "slices": slices,
    }
