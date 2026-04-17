from __future__ import annotations

from collections import Counter


def count_statuses(rows: list[dict[str, object]], key: str) -> Counter:
    return Counter(str(row.get(key, "")) for row in rows)


def bool_count(rows: list[dict[str, object]], key: str, value: bool = True) -> int:
    return sum(1 for row in rows if row.get(key) is value)
