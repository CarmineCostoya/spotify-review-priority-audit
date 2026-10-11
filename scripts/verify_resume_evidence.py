#!/usr/bin/env python3
"""Verify the official interruption/resume evidence without model or network calls."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check saved interruption/resume evidence from the official run."
    )
    parser.add_argument("--grading-dir", default="grading")
    args = parser.parse_args()

    grading = Path(args.grading_dir)
    before = set(load_json(grading / "checkpoint_before.json")["completed_ids"])
    after = set(load_json(grading / "checkpoint_after.json")["completed_ids"])
    calls = load_jsonl(grading / "calls.jsonl")

    resumed_enrichment_calls = [
        call
        for call in calls
        if call.get("phase") == "resume" and call.get("role") == "enrich"
    ]
    resumed_review_ids = {
        review_id
        for call in resumed_enrichment_calls
        for review_id in call.get("review_ids", [])
    }
    repeated_completed_ids = before & resumed_review_ids
    new_completed_ids = after - before
    removed_completed_ids = before - after

    checks = {
        "resume_added_completed_work": bool(new_completed_ids),
        "no_previously_completed_id_was_reenriched": not repeated_completed_ids,
        "no_completed_id_disappeared": not removed_completed_ids,
    }
    passed = all(checks.values())

    print("OFFICIAL INTERRUPTION / RESUME EVIDENCE")
    print("=" * 42)
    print(f"Completed before interruption:       {len(before):,}")
    print(f"Completed after recovery:            {len(after):,}")
    print(f"Newly completed after resume:        {len(new_completed_ids):,}")
    print(f"Resume enrichment calls logged:      {len(resumed_enrichment_calls):,}")
    print(f"Unique IDs in resume enrich calls:   {len(resumed_review_ids):,}")
    print(f"Previously completed IDs resubmitted:{len(repeated_completed_ids):>10,}")
    print(f"Completed IDs lost after resume:     {len(removed_completed_ids):,}")
    print()
    for name, result in checks.items():
        print(f"[{'PASS' if result else 'FAIL'}] {name.replace('_', ' ')}")
    print()
    print("FINAL RESULT:", "PASS" if passed else "FAIL")

    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
