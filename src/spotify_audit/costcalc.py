from __future__ import annotations

import csv
import json
from decimal import Decimal
from pathlib import Path

from .io_utils import read_jsonl


def calculate(calls_path: str, rates_path: str, projected_records: int) -> dict:
    rates = {}
    with Path(rates_path).open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            rates[(row["model"], row["unit"])] = Decimal(row["price_per_unit"])
    calls = list(read_jsonl(calls_path))
    api_calls = [c for c in calls if c.get("measured_api_call")]
    completed_ids = {rid for call in api_calls if call.get("role") == "enrich" and call.get("outcome") == "succeeded" for rid in call.get("review_ids", [])}
    totals = {"uncached_input_tokens": 0, "cached_input_tokens": 0, "output_tokens": 0}
    cost = Decimal("0")
    missing_usage = 0
    for call in api_calls:
        model = call.get("model", "")
        input_tokens = call.get("input_tokens")
        output_tokens = call.get("output_tokens")
        cached = call.get("cached_input_tokens") or 0
        if input_tokens is None or output_tokens is None:
            missing_usage += 1
            continue
        uncached = max(0, int(input_tokens) - int(cached))
        totals["uncached_input_tokens"] += uncached
        totals["cached_input_tokens"] += int(cached)
        totals["output_tokens"] += int(output_tokens)
        cost += Decimal(uncached) * rates.get((model, "input_token"), Decimal("0"))
        cost += Decimal(cached) * rates.get((model, "cached_input_token"), Decimal("0"))
        cost += Decimal(output_tokens) * rates.get((model, "output_token"), Decimal("0"))
    per_record = cost / len(completed_ids) if completed_ids else None
    return {
        "pilot_status": "measured" if api_calls and completed_ids and not missing_usage else "pending_or_incomplete",
        "measured_api_calls": len(api_calls),
        "completed_pilot_records": len(completed_ids),
        "missing_usage_calls": missing_usage,
        **totals,
        "measured_api_cost_usd": str(cost.quantize(Decimal("0.000001"))),
        "cost_per_completed_record_usd": str(per_record.quantize(Decimal("0.000001"))) if per_record is not None else "unknown",
        "projected_records": projected_records,
        "projected_variable_api_cost_usd": str((per_record * projected_records).quantize(Decimal("0.01"))) if per_record is not None else "unknown",
    }


def write_report(result: dict, path: str) -> None:
    lines = ["# Offline cost replay", "", "This report is computed from saved usage and editable rates; it makes no API calls.", ""]
    for key, value in result.items():
        lines.append(f"- **{key.replace('_', ' ')}:** {value}")
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")
