from __future__ import annotations

import csv
import json
import sqlite3
from pathlib import Path

from .io_utils import iter_csv, read_jsonl


SCHEMA = """
CREATE TABLE IF NOT EXISTS reviews (
  review_id TEXT PRIMARY KEY,
  review_text TEXT NOT NULL,
  review_rating TEXT,
  review_likes TEXT,
  app_version TEXT,
  review_timestamp TEXT,
  source_sha256 TEXT NOT NULL,
  status TEXT NOT NULL,
  topic TEXT,
  intent TEXT,
  sentiment REAL,
  severity INTEGER,
  evidence_quote TEXT,
  needs_review INTEGER,
  label_config TEXT,
  quarantine_reason TEXT
);
CREATE TABLE IF NOT EXISTS issue_membership (
  issue_id TEXT NOT NULL,
  review_id TEXT NOT NULL,
  PRIMARY KEY(issue_id, review_id),
  FOREIGN KEY(review_id) REFERENCES reviews(review_id)
);
CREATE TABLE IF NOT EXISTS ranking (
  rank INTEGER PRIMARY KEY,
  issue_id TEXT UNIQUE NOT NULL,
  complaint_count INTEGER NOT NULL,
  severity_sum INTEGER NOT NULL,
  mean_severity REAL NOT NULL,
  priority_score INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
"""


def build_database(input_csv: str, run_dir: str, database: str) -> dict:
    run = Path(run_dir)
    records = {r["review_id"]: r for r in read_jsonl(run / "records.jsonl")}
    target = Path(database)
    target.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(target)
    connection.executescript(SCHEMA)
    connection.execute("DELETE FROM reviews")
    connection.execute("DELETE FROM issue_membership")
    connection.execute("DELETE FROM ranking")
    inserted = 0
    for source in iter_csv(input_csv):
        record = records.get(source["review_id"])
        if not record:
            continue
        connection.execute(
            "INSERT INTO reviews VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                source["review_id"], source["review_text"], source["review_rating"], source["review_likes"],
                source["app_version"], source["review_timestamp"], record["source_sha256"], record["status"],
                record.get("topic"), record.get("intent"), record.get("sentiment"), record.get("severity"),
                record.get("evidence_quote"), int(record.get("needs_review", False)), record.get("label_config"), record.get("reason"),
            ),
        )
        inserted += 1
    with (run / "membership.csv").open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            connection.execute("INSERT INTO issue_membership VALUES (?,?)", (row["issue_id"], row["review_id"]))
    with (run / "ranking.csv").open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            connection.execute("INSERT INTO ranking VALUES (?,?,?,?,?,?)", tuple(row[key] for key in ("rank", "issue_id", "complaint_count", "severity_sum", "mean_severity", "priority_score")))
    summary = json.loads((run / "run_summary.json").read_text(encoding="utf-8"))
    for key, value in summary.items():
        connection.execute("INSERT OR REPLACE INTO metadata VALUES (?,?)", (key, json.dumps(value)))
    connection.commit(); connection.close()
    return {"database": str(target), "reviews_inserted": inserted}
