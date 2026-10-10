from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

from .io_utils import atomic_json, read_jsonl


def evaluate_golden(golden_csv: str, predictions_jsonl: str, out: str) -> dict:
    with Path(golden_csv).open("r", encoding="utf-8", newline="") as handle:
        expected = {row["review_id"]: row for row in csv.DictReader(handle)}
    required = ("topic", "intent", "severity")
    unlabeled = [rid for rid, row in expected.items() if any(not row.get(field, "").strip() for field in required)]
    if unlabeled:
        raise ValueError(f"golden set still has {len(unlabeled)} unlabeled rows; human labeling is required first")
    predictions = {row["review_id"]: row for row in read_jsonl(predictions_jsonl)}
    details = []
    topic_correct = intent_correct = severity_exact = 0
    severity_error = 0.0
    confusion: dict[str, Counter] = defaultdict(Counter)
    for rid, truth in expected.items():
        pred = predictions.get(rid)
        if not pred or pred.get("status") != "completed":
            details.append({"review_id": rid, "missing_prediction": True})
            continue
        topic_match = pred.get("topic") == truth["topic"]
        intent_match = pred.get("intent") == truth["intent"]
        expected_severity = int(truth["severity"])
        severity_match = int(pred.get("severity", -1)) == expected_severity
        error = abs(int(pred.get("severity", -1)) - expected_severity)
        topic_correct += topic_match; intent_correct += intent_match; severity_exact += severity_match; severity_error += error
        confusion[truth["topic"]][pred.get("topic", "missing")] += 1
        details.append({"review_id": rid, "topic_match": topic_match, "intent_match": intent_match, "severity_exact": severity_match, "severity_absolute_error": error})
    n = len(expected)
    result = {
        "sample_size": n,
        "missing_predictions": sum(d.get("missing_prediction", False) for d in details),
        "topic_agreement": topic_correct / n,
        "intent_agreement": intent_correct / n,
        "severity_exact_agreement": severity_exact / n,
        "severity_mean_absolute_error": severity_error / n,
        "topic_confusion": {key: dict(value) for key, value in sorted(confusion.items())},
        "details": details,
    }
    atomic_json(out, result)
    return result

