from __future__ import annotations

import shutil
from pathlib import Path

from .io_utils import atomic_json, file_sha256, profile_csv


def export_grading(input_csv: str, run_dir: str, grading_dir: str) -> dict:
    run = Path(run_dir)
    out = Path(grading_dir)
    out.mkdir(parents=True, exist_ok=True)
    profile = profile_csv(input_csv)
    atomic_json(out / "run.json", {
        "version": "a5-audit-v1",
        "analysis_count": profile["records"],
        "analysis_sha256": file_sha256(input_csv),
        "classification_input_fields": ["review_text"],
        "allow_multi_issue": False,
        "scope_note": "100,000 nonempty reviews per professor's in-class requirement update",
    })
    atomic_json(out / "ingestion.json", profile)
    mapping = {
        "records.jsonl": "records.jsonl",
        "membership.csv": "membership.csv",
        "ranking.csv": "ranking.csv",
        "claims.csv": "claims.csv",
        "calls.jsonl": "calls.jsonl",
        "checkpoint_before.json": "checkpoint_before.json",
        "checkpoint_after.json": "checkpoint_after.json",
    }
    missing = []
    for source_name, target_name in mapping.items():
        source = run / source_name
        if source.exists():
            shutil.copyfile(source, out / target_name)
        else:
            missing.append(source_name)
    return {"grading_dir": str(out), "analysis_count": profile["records"], "missing": missing}

