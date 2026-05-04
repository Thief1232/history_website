from collections import Counter
from math import cos, radians, sin
from typing import Any, TypedDict


CHART_TYPES = ("bar", "plot", "stem", "stackplot", "stairs", "boxplot", "violinplot", "pie")
CHART_LABELS = {
    "bar": "Bar",
    "plot": "Plot",
    "stem": "Stem",
    "stackplot": "Stackplot",
    "stairs": "Stairs",
    "boxplot": "Boxplot",
    "violinplot": "Violinplot",
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
    visits = [item["visits"] for item in chart_data]
    return {
        "type": normalize_chart_type(chart_type),
        "rows": build_chart_rows(chart_data),
        "svg": build_svg_model(chart_data),
        "pie": build_pie_model(chart_data),
        "boxplot": build_boxplot_model(visits),
        "violinplot": build_violin_model(visits),
    }


def build_svg_model(chart_data: list[ChartItem]) -> dict[str, Any]:
    width = 900
    height = 360
    padding = 44
    base_y = height - padding
    max_visits = max((item["visits"] for item in chart_data), default=0)

    points = []
    for index, item in enumerate(chart_data):
        x = _scale_index(index, len(chart_data), padding, width - padding)
        y = base_y if max_visits == 0 else base_y - (item["visits"] / max_visits) * (height - padding * 2)
        points.append({"x": x, "y": y, "domain": item["domain"], "visits": item["visits"]})

    polyline = _points_attr(points)
    area = f"{padding},{base_y} {polyline} {width - padding},{base_y}" if points else ""
    stairs = _stairs_path(points)

    return {
        "width": width,
        "height": height,
        "padding": padding,
        "base_y": base_y,
        "points": points,
        "polyline": polyline,
        "area": area,
        "stairs": stairs,
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


def build_boxplot_model(values: list[int]) -> dict[str, float]:
    if not values:
        return {"min": 0, "q1": 0, "median": 0, "q3": 0, "max": 0}

    ordered = sorted(values)
    return {
        "min": _scale_value(ordered[0], ordered[-1], ordered[0]),
        "q1": _scale_value(_percentile(ordered, 0.25), ordered[-1], ordered[0]),
        "median": _scale_value(_percentile(ordered, 0.5), ordered[-1], ordered[0]),
        "q3": _scale_value(_percentile(ordered, 0.75), ordered[-1], ordered[0]),
        "max": _scale_value(ordered[-1], ordered[-1], ordered[0]),
    }


def build_violin_model(values: list[int]) -> dict[str, str]:
    if not values:
        return {"path": ""}

    bins = 7
    minimum = min(values)
    maximum = max(values)
    spread = max(maximum - minimum, 1)
    counts = [0] * bins

    for value in values:
        index = min(bins - 1, int((value - minimum) / spread * bins))
        counts[index] += 1

    max_count = max(counts) or 1
    center_x = 450
    top = 58
    bottom = 302
    height = bottom - top
    left_points = []
    right_points = []

    for index, count in enumerate(counts):
        y = top + (index / (bins - 1)) * height
        half_width = 18 + (count / max_count) * 150
        left_points.append((center_x - half_width, y))
        right_points.append((center_x + half_width, y))

    all_points = left_points + list(reversed(right_points))
    path = "M " + " L ".join(f"{x:.2f} {y:.2f}" for x, y in all_points) + " Z"
    return {"path": path}


def _scale_index(index: int, total: int, start: int, end: int) -> float:
    if total <= 1:
        return (start + end) / 2
    return start + (index / (total - 1)) * (end - start)


def _points_attr(points: list[dict[str, Any]]) -> str:
    return " ".join(f"{point['x']:.2f},{point['y']:.2f}" for point in points)


def _stairs_path(points: list[dict[str, Any]]) -> str:
    if not points:
        return ""

    path = f"M {points[0]['x']:.2f} {points[0]['y']:.2f}"
    for point in points[1:]:
        path += f" H {point['x']:.2f} V {point['y']:.2f}"
    return path


def _percentile(values: list[int], fraction: float) -> float:
    if len(values) == 1:
        return float(values[0])

    position = (len(values) - 1) * fraction
    lower = int(position)
    upper = min(lower + 1, len(values) - 1)
    weight = position - lower
    return values[lower] * (1 - weight) + values[upper] * weight


def _scale_value(value: float, maximum: int, minimum: int) -> float:
    if maximum == minimum:
        return 50.0
    return 8 + ((value - minimum) / (maximum - minimum)) * 84
