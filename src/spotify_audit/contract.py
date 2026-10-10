from __future__ import annotations

import hashlib
import json
from decimal import Decimal, ROUND_HALF_UP

SOURCE_FIELDS = (
    "review_id",
    "review_text",
    "review_rating",
    "review_likes",
    "app_version",
    "review_timestamp",
)
TOPICS = ("access", "usability", "playback", "downloads", "catalog", "billing", "support", "other")
INTENTS = ("cancellation", "complaint", "request", "praise", "unclear")
STATUSES = ("pending", "completed", "quarantined")
LABEL_CONFIG_HEURISTIC = "local-heuristic+labels-v1+record-v1"


def row_sha(row: dict[str, str]) -> str:
    values = [str(row.get(field, "")) for field in SOURCE_FIELDS]
    packed = json.dumps(values, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(packed.encode("utf-8")).hexdigest()


def validate_record(record: dict, source: dict[str, str] | None = None) -> list[str]:
    errors: list[str] = []
    if not record.get("review_id"):
        errors.append("missing review_id")
    if record.get("status") not in STATUSES:
        errors.append("invalid status")
    if record.get("status") == "quarantined":
        if not record.get("reason"):
            errors.append("quarantined record needs reason")
        return errors
    if record.get("status") != "completed":
        return errors
    if record.get("topic") not in TOPICS:
        errors.append("invalid topic")
    if record.get("intent") not in INTENTS:
        errors.append("invalid intent")
    if not isinstance(record.get("severity"), int) or not 1 <= record["severity"] <= 5:
        errors.append("severity must be integer 1..5")
    if not isinstance(record.get("sentiment"), (int, float)) or not -1 <= record["sentiment"] <= 1:
        errors.append("sentiment must be within -1..1")
    if not isinstance(record.get("entities"), list):
        errors.append("entities must be a list")
    if not isinstance(record.get("needs_review"), bool):
        errors.append("needs_review must be boolean")
    if not record.get("label_config"):
        errors.append("missing label_config")
    quote = record.get("evidence_quote")
    if not isinstance(quote, str) or not quote:
        errors.append("missing evidence_quote")
    if source is not None:
        if record.get("review_id") != source.get("review_id"):
            errors.append("review_id does not match source")
        if record.get("source_sha256") != row_sha(source):
            errors.append("source_sha256 does not match source")
        if quote and quote not in source.get("review_text", ""):
            errors.append("evidence_quote is not an exact source substring")
    return errors


def six_decimal(value: Decimal) -> str:
    return str(value.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP))

