from __future__ import annotations

import csv
import json
import random
import time
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

from .contract import row_sha, six_decimal, validate_record
from .io_utils import append_jsonl, atomic_json, iter_csv, read_jsonl, write_jsonl
from .providers import HeuristicProvider, OpenAIProvider, issue_for


def batched(items, size: int):
    batch = []
    for item in items:
        batch.append(item)
        if len(batch) == size:
            yield batch
            batch = []
    if batch:
        yield batch


def run_pipeline(
    input_csv: str,
    run_dir: str,
    provider_name: str = "heuristic",
    batch_size: int = 25,
    verify_count: int = 10,
    phase: str = "initial",
    max_records: int | None = None,
) -> dict:
    if not 1 <= batch_size <= 50:
        raise ValueError("batch_size must be between 1 and 50")
    root = Path(run_dir)
    root.mkdir(parents=True, exist_ok=True)
    records_path = root / "records.jsonl"
    calls_path = root / "calls.jsonl"
    provider = HeuristicProvider() if provider_name == "heuristic" else OpenAIProvider()
    completed = {r["review_id"]: r for r in read_jsonl(records_path)}
    if phase == "resume":
        atomic_json(root / "checkpoint_before.json", {"completed_ids": sorted(rid for rid, record in completed.items() if record.get("status") == "completed")})
    source_rows: dict[str, dict[str, str]] = {}
    pending = []
    pending_source_by_text: dict[str, str] = {}
    aliases_by_source_id: dict[str, list[dict[str, str]]] = defaultdict(list)
    cache_by_text: dict[str, dict] = {}
    for row in iter_csv(input_csv):
        if max_records is not None and len(source_rows) >= max_records:
            break
        source_rows[row["review_id"]] = row
        if row["review_id"] in completed:
            rec = completed[row["review_id"]]
            if rec.get("status") == "completed" and not rec.get("cache_source_id"):
                cache_by_text[row["review_text"]] = rec
            continue
        if not row["review_text"].strip():
            rec = {"review_id": row["review_id"], "source_sha256": row_sha(row), "status": "quarantined", "reason": "empty_review_text"}
            append_jsonl(records_path, rec)
            completed[row["review_id"]] = rec
            continue
        cached = cache_by_text.get(row["review_text"])
        if cached and cached.get("label_config") == provider.label_config:
            rec = {k: v for k, v in cached.items() if k != "review_id" and k != "source_sha256"}
            rec.update({"review_id": row["review_id"], "source_sha256": row_sha(row), "cache_source_id": cached["review_id"]})
            append_jsonl(records_path, rec)
            completed[row["review_id"]] = rec
            continue
        pending_source_id = pending_source_by_text.get(row["review_text"])
        if pending_source_id:
            aliases_by_source_id[pending_source_id].append(row)
            continue
        pending.append(row)
        pending_source_by_text[row["review_text"]] = row["review_id"]

    started = time.perf_counter()
    failures = 0
    for batch in batched(pending, batch_size):
        try:
            outputs, call = provider.classify_batch(batch, role="enrich")
            call["phase"] = phase
            append_jsonl(calls_path, call)
            by_id = {r["review_id"]: r for r in batch}
            for record in outputs:
                errors = validate_record(record, by_id.get(record.get("review_id")))
                if errors:
                    raise ValueError("; ".join(errors))
            for record in outputs:
                append_jsonl(records_path, record)
                completed[record["review_id"]] = record
                cache_by_text[by_id[record["review_id"]]["review_text"]] = record
                for alias_row in aliases_by_source_id.get(record["review_id"], []):
                    alias = {k: v for k, v in record.items() if k not in ("review_id", "source_sha256")}
                    alias.update({"review_id": alias_row["review_id"], "source_sha256": row_sha(alias_row), "cache_source_id": record["review_id"]})
                    append_jsonl(records_path, alias)
                    completed[alias_row["review_id"]] = alias
        except Exception as exc:
            failures += len(batch)
            append_jsonl(calls_path, {
                "request_id": f"failed-{int(time.time() * 1000)}",
                "role": "enrich",
                "review_ids": [r["review_id"] for r in batch],
                "model": provider.model,
                "phase": phase,
                "outcome": "failed",
                "label_config": provider.label_config,
                "error": str(exc),
                "input_tokens": 0,
                "output_tokens": 0,
            })
            for row in batch:
                failed_rows = [row, *aliases_by_source_id.get(row["review_id"], [])]
                for failed_row in failed_rows:
                    rec = {"review_id": failed_row["review_id"], "source_sha256": row_sha(failed_row), "status": "quarantined", "reason": "classification_failed", "attempts": 1}
                    append_jsonl(records_path, rec)
                    completed[failed_row["review_id"]] = rec

    final_records = [completed[rid] for rid in source_rows]
    write_jsonl(records_path, final_records)
    completed_records = [r for r in final_records if r["status"] == "completed"]

    rng = random.Random(20261010)
    sample = rng.sample(completed_records, min(verify_count, len(completed_records)))
    verify_rows = [source_rows[r["review_id"]] for r in sample]
    verifier_records = []
    for verify_batch in batched(verify_rows, 50):
        batch_records, verifier_call = provider.classify_batch(verify_batch, role="verify")
        verifier_call["phase"] = phase
        append_jsonl(calls_path, verifier_call)
        verifier_records.extend(batch_records)
    write_jsonl(root / "verification.jsonl", verifier_records)
    original_by_id = {r["review_id"]: r for r in sample}
    disagreements = []
    for record in verifier_records:
        original = original_by_id[record["review_id"]]
        changed = [key for key in ("topic", "intent", "severity") if original.get(key) != record.get(key)]
        if changed:
            disagreements.append({"review_id": record["review_id"], "fields": changed, "enricher": original, "verifier": record})
    atomic_json(root / "verification_report.json", {"sample_size": len(sample), "disagreement_count": len(disagreements), "disagreements": disagreements})

    memberships = []
    for record in completed_records:
        if record["intent"] in ("complaint", "cancellation"):
            memberships.append({"issue_id": issue_for(record, source_rows[record["review_id"]]["review_text"]), "review_id": record["review_id"]})
    with (root / "membership.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["issue_id", "review_id"], lineterminator="\n")
        writer.writeheader(); writer.writerows(memberships)

    ranking = rank_records(completed_records, memberships)
    write_ranking(root / "ranking.csv", ranking)
    memo = write_memo(root / "memo.md", ranking, memberships)
    claims = []
    for item in ranking[:3]:
        for metric in ("complaint_count", "severity_sum", "mean_severity", "priority_score"):
            claims.append({"claim_id": f"CLAIM-{len(claims)+1:03d}", "issue_id": item["issue_id"], "metric": metric, "value": item[metric]})
    with (root / "claims.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["claim_id", "issue_id", "metric", "value"], lineterminator="\n")
        writer.writeheader(); writer.writerows(claims)
    append_jsonl(calls_path, {"request_id": f"local-group-{time.time_ns()}", "role": "group", "review_ids": [], "model": "deterministic-code-v1", "phase": phase, "outcome": "succeeded", "label_config": provider.label_config, "input_tokens": 0, "output_tokens": 0, "measured_api_call": False})
    append_jsonl(calls_path, {"request_id": f"local-memo-{time.time_ns()}", "role": "memo", "review_ids": [], "model": "deterministic-template-v1", "phase": phase, "outcome": "succeeded", "label_config": provider.label_config, "input_tokens": 0, "output_tokens": 0, "measured_api_call": False})

    summary = {
        "input_csv": input_csv,
        "provider": provider_name,
        "label_config": provider.label_config,
        "source_records": len(source_rows),
        "completed": len(completed_records),
        "quarantined": sum(r["status"] == "quarantined" for r in final_records),
        "failures_this_run": failures,
        "issue_count": len(ranking),
        "verification_sample": len(sample),
        "verification_disagreements": len(disagreements),
        "elapsed_seconds": round(time.perf_counter() - started, 6),
        "memo": memo,
    }
    atomic_json(root / "run_summary.json", summary)
    atomic_json(root / "checkpoint_after.json", {"completed_ids": sorted(r["review_id"] for r in final_records if r.get("status") == "completed")})
    if phase == "initial" and not (root / "checkpoint_before.json").exists():
        atomic_json(root / "checkpoint_before.json", {"completed_ids": []})
    return summary


def rank_records(records: list[dict], memberships: list[dict]) -> list[dict]:
    by_id = {r["review_id"]: r for r in records}
    grouped: dict[str, list[dict]] = defaultdict(list)
    for member in memberships:
        record = by_id.get(member["review_id"])
        if record and record.get("intent") in ("complaint", "cancellation"):
            grouped[member["issue_id"]].append(record)
    output = []
    for issue_id, members in grouped.items():
        count = len(members)
        severity_sum = sum(int(r["severity"]) for r in members)
        output.append({
            "issue_id": issue_id,
            "complaint_count": str(count),
            "severity_sum": str(severity_sum),
            "mean_severity": six_decimal(Decimal(severity_sum) / Decimal(count)),
            "priority_score": str(severity_sum),
        })
    output.sort(key=lambda r: (-int(r["priority_score"]), r["issue_id"]))
    for index, row in enumerate(output, 1):
        row["rank"] = str(index)
    return output


def write_ranking(path: Path, ranking: list[dict]) -> None:
    fields = ["rank", "issue_id", "complaint_count", "severity_sum", "mean_severity", "priority_score"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader(); writer.writerows(ranking)


def write_memo(path: Path, ranking: list[dict], memberships: list[dict]) -> str:
    if not ranking:
        text = "# Product priority memo\n\nNo complaint or cancellation issues were available for ranking.\n"
    else:
        top = ranking[0]
        examples = [m["review_id"] for m in memberships if m["issue_id"] == top["issue_id"]][:5]
        alternatives = ", ".join(row["issue_id"] for row in ranking[1:3]) or "none"
        text = (
            "# Product priority memo\n\n"
            f"## Recommendation\n\nPrioritize **{top['issue_id']}**. It ranks first with {top['complaint_count']} "
            f"complaint/cancellation reviews, mean severity {top['mean_severity']}, and priority score {top['priority_score']}.\n\n"
            f"Representative review IDs: {', '.join(examples) or 'none'}.\n\n"
            f"## Alternatives\n\nThe next ranked issues are {alternatives}.\n\n"
            "## Limitations\n\nThese are self-selected historical app-store reviews. They do not establish revenue impact, "
            "confirmed churn, or causal effects. Any unresolved or quarantined records must be disclosed before final submission.\n"
        )
    path.write_text(text, encoding="utf-8")
    return str(path)
