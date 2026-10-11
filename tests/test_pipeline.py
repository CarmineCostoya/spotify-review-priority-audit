import csv
import json
import tempfile
import unittest
from pathlib import Path

from spotify_audit.contract import row_sha, validate_record
from spotify_audit.pipeline import rank_records, run_pipeline
from spotify_audit.database import build_database
from spotify_audit.providers import OpenAIProvider, issue_for


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

    def test_ads_issue_uses_whole_word_not_substring(self):
        record = {"topic": "usability"}
        self.assertEqual(issue_for(record, "Too many ads interrupt playback"), "USABILITY-ADS")
        self.assertEqual(issue_for(record, "The app will not load"), "USABILITY-GENERAL")
        self.assertEqual(issue_for(record, "Please add a feature"), "USABILITY-GENERAL")

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

    def test_pipeline_resume_retries_classification_failures(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "input.csv"
            row = ["r1", "Cannot log in", "1", "0", "", "2023-01-01 00:00:00"]
            with source.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle); writer.writerow(FIELDS); writer.writerow(row)
            run_dir = root / "run"
            run_dir.mkdir()
            failed = {
                "review_id": "r1",
                "source_sha256": row_sha(dict(zip(FIELDS, row))),
                "status": "quarantined",
                "reason": "classification_failed",
                "attempts": 1,
            }
            (run_dir / "records.jsonl").write_text(json.dumps(failed) + "\n", encoding="utf-8")

            resumed = run_pipeline(str(source), str(run_dir), verify_count=0, phase="resume")

            self.assertEqual(resumed["completed"], 1)
            self.assertEqual(resumed["quarantined"], 0)
            saved = [json.loads(line) for line in (run_dir / "records.jsonl").read_text().splitlines()]
            self.assertEqual(saved[0]["status"], "completed")

    def test_pipeline_supports_bounded_parallel_workers(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "input.csv"
            rows = [
                [f"r{i}", f"Review number {i}", "3", "0", "", "2023-01-01 00:00:00"]
                for i in range(4)
            ]
            with source.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle); writer.writerow(FIELDS); writer.writerows(rows)
            run_dir = root / "run"

            result = run_pipeline(str(source), str(run_dir), batch_size=2, verify_count=0, workers=2)

            self.assertEqual(result["completed"], 4)
            self.assertEqual(result["quarantined"], 0)
            calls = [json.loads(line) for line in (run_dir / "calls.jsonl").read_text().splitlines()]
            self.assertEqual(sum(call.get("role") == "enrich" for call in calls), 2)


if __name__ == "__main__":
    unittest.main()
