from __future__ import annotations

import csv
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Iterable, Iterator

from .contract import SOURCE_FIELDS, row_sha


def iter_csv(path: str | Path) -> Iterator[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = set(SOURCE_FIELDS) - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"CSV is missing columns: {sorted(missing)}")
        for raw in reader:
            yield {field: raw.get(field, "") for field in SOURCE_FIELDS}


def file_sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def atomic_json(path: str | Path, payload) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=target.parent, delete=False) as tmp:
        json.dump(payload, tmp, ensure_ascii=False, indent=2, sort_keys=True)
        tmp.write("\n")
        temp_name = tmp.name
    os.replace(temp_name, target)


def write_jsonl(path: str | Path, records: Iterable[dict]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=target.parent, delete=False) as tmp:
        for record in records:
            tmp.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
        temp_name = tmp.name
    os.replace(temp_name, target)


def append_jsonl(path: str | Path, record: dict) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def read_jsonl(path: str | Path) -> Iterator[dict]:
    target = Path(path)
    if not target.exists():
        return
    with target.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def profile_csv(path: str | Path) -> dict:
    count = empty = missing_version = duplicate_ids = 0
    seen_ids: set[str] = set()
    ratings: dict[str, int] = {}
    months: dict[str, int] = {}
    distinct_texts: set[str] = set()
    nonempty = 0
    for row in iter_csv(path):
        count += 1
        rid = row["review_id"]
        if rid in seen_ids:
            duplicate_ids += 1
        seen_ids.add(rid)
        text = row["review_text"]
        if text.strip():
            nonempty += 1
            distinct_texts.add(text)
        else:
            empty += 1
        if not row["app_version"].strip():
            missing_version += 1
        ratings[row["review_rating"]] = ratings.get(row["review_rating"], 0) + 1
        month = row["review_timestamp"][:7]
        months[month] = months.get(month, 0) + 1
    return {
        "source_path": str(Path(path)),
        "source_bytes": Path(path).stat().st_size,
        "source_sha256": file_sha256(path),
        "records": count,
        "nonempty_review_text": nonempty,
        "empty_review_text": empty,
        "missing_app_version": missing_version,
        "duplicate_review_ids": duplicate_ids,
        "distinct_nonempty_texts": len(distinct_texts),
        "reviews_by_rating": dict(sorted(ratings.items())),
        "reviews_by_month": dict(sorted(months.items())),
    }


def select_nonempty(path: str | Path, out: str | Path, count: int) -> dict:
    target = Path(out)
    target.parent.mkdir(parents=True, exist_ok=True)
    selected = 0
    with target.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=SOURCE_FIELDS, lineterminator="\n")
        writer.writeheader()
        for row in iter_csv(path):
            if not row["review_text"].strip():
                continue
            writer.writerow(row)
            selected += 1
            if selected == count:
                break
    if selected != count:
        raise ValueError(f"requested {count} nonempty records but found {selected}")
    return {
        "selection_method": "first nonempty rows in source order",
        "selected_nonempty": selected,
        "output_path": str(target),
        "output_sha256": file_sha256(target),
    }


def source_with_hash(row: dict[str, str]) -> dict[str, str]:
    enriched = dict(row)
    enriched["source_sha256"] = row_sha(row)
    return enriched

