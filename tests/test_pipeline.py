import csv
import json
import tempfile
import unittest
from pathlib import Path

from spotify_audit.contract import row_sha, validate_record
from spotify_audit.pipeline import rank_records, run_pipeline
from spotify_audit.database import build_database
from spotify_audit.providers import OpenAIProvider


FIELDS = ["review_id", "review_text", "review_rating", "review_likes", "app_version", "review_timestamp"]


class PipelineTests(unittest.TestCase):
    def test_paid_provider_is_locked_by_default(self):
        row = dict(zip(FIELDS, ["r1", "hello", "5", "0", "", "2023-01-01 00:00:00"]))
        with self.assertRaisesRegex(RuntimeError, "paid calls are locked"):
            OpenAIProvider().classify_batch([row])

    def test_row_hash_is_stable(self):
        row = dict(zip(FIELDS, ["r1", "hello", "5", "0", "", "2023-01-01 00:00:00"]))
        self.assertEqual(row_sha(row), row_sha(dict(row)))

    def test_quote_must_be_substring(self):
        source = dict(zip(FIELDS, ["r1", "songs stop offline", "1", "0", "1.0", "2023-01-01 00:00:00"]))
        record = {"review_id": "r1", "source_sha256": row_sha(source), "status": "completed", "topic": "downloads", "intent": "complaint", "sentiment": -0.5, "severity": 3, "entities": [], "evidence_quote": "invented", "needs_review": False, "label_config": "test"}
        self.assertIn("evidence_quote is not an exact source substring", validate_record(record, source))

    def test_ranking_tie_break(self):
        records = [
            {"review_id": "a", "intent": "complaint", "severity": 3},
            {"review_id": "b", "intent": "cancellation", "severity": 3},
        ]
        ranking = rank_records(records, [{"issue_id": "Z", "review_id": "a"}, {"issue_id": "A", "review_id": "b"}])
        self.assertEqual([r["issue_id"] for r in ranking], ["A", "Z"])
        self.assertEqual(ranking[0]["mean_severity"], "3.000000")

    def test_pipeline_resume_avoids_new_enrichment(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "input.csv"
            rows = [
                ["r1", "Cannot log in", "1", "0", "", "2023-01-01 00:00:00"],
                ["r2", "Cannot log in", "1", "0", "", "2023-01-02 00:00:00"],
                ["r3", "", "1", "0", "", "2023-01-03 00:00:00"],
            ]
            with source.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle); writer.writerow(FIELDS); writer.writerows(rows)
            run_dir = root / "run"
            first = run_pipeline(str(source), str(run_dir), verify_count=0)
            calls_before = (run_dir / "calls.jsonl").read_text().count('"role":"enrich"')
            second = run_pipeline(str(source), str(run_dir), verify_count=0, phase="resume")
            calls_after = (run_dir / "calls.jsonl").read_text().count('"role":"enrich"')
            self.assertEqual(first["completed"], 2)
            self.assertEqual(first["quarantined"], 1)
            self.assertEqual(calls_before, calls_after)
            self.assertEqual(second["source_records"], 3)
            self.assertEqual(json.loads((run_dir / "checkpoint_before.json").read_text())["completed_ids"], ["r1", "r2"])
            self.assertEqual(json.loads((run_dir / "checkpoint_after.json").read_text())["completed_ids"], ["r1", "r2"])
            result = build_database(str(source), str(run_dir), str(root / "audit.db"))
            self.assertEqual(result["reviews_inserted"], 3)


if __name__ == "__main__":
    unittest.main()
