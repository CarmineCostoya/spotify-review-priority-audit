from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from .costcalc import calculate, write_report
from .database import build_database
from .evaluation import evaluate_golden
from .export import export_grading
from .io_utils import atomic_json, profile_csv, select_nonempty
from .pipeline import run_pipeline
from .server import serve


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="spotify-audit")
    commands = root.add_subparsers(dest="command", required=True)
    profile = commands.add_parser("profile")
    profile.add_argument("--input", required=True); profile.add_argument("--out", required=True)
    select = commands.add_parser("select")
    select.add_argument("--input", required=True); select.add_argument("--out", required=True); select.add_argument("--count", type=int, default=100000)
    run = commands.add_parser("run")
    run.add_argument("--input", required=True); run.add_argument("--run-dir", required=True)
    run.add_argument("--provider", choices=("heuristic", "openai"), default="heuristic")
    run.add_argument("--batch-size", type=int, default=25); run.add_argument("--verify-count", type=int, default=10)
    run.add_argument("--phase", choices=("initial", "resume"), default="initial"); run.add_argument("--max-records", type=int)
    run.add_argument("--allow-paid", action="store_true")
    db = commands.add_parser("database")
    db.add_argument("--input", required=True); db.add_argument("--run-dir", required=True); db.add_argument("--database", required=True)
    cost = commands.add_parser("cost")
    cost.add_argument("--calls", required=True); cost.add_argument("--rates", required=True); cost.add_argument("--out", required=True); cost.add_argument("--projected-records", type=int, default=100000)
    server = commands.add_parser("serve")
    server.add_argument("--database", required=True); server.add_argument("--port", type=int, default=8000)
    evaluation = commands.add_parser("evaluate")
    evaluation.add_argument("--golden", required=True); evaluation.add_argument("--predictions", required=True); evaluation.add_argument("--out", required=True)
    export = commands.add_parser("export")
    export.add_argument("--input", required=True); export.add_argument("--run-dir", required=True); export.add_argument("--grading-dir", required=True)
    return root


def main() -> None:
    args = parser().parse_args()
    if args.command == "profile":
        result = profile_csv(args.input); atomic_json(args.out, result)
    elif args.command == "select":
        result = select_nonempty(args.input, args.out, args.count); atomic_json(Path(args.out).with_suffix(".selection.json"), result)
    elif args.command == "run":
        if args.allow_paid:
            os.environ["ALLOW_PAID_MODEL_CALLS"] = "yes"
        result = run_pipeline(args.input, args.run_dir, args.provider, args.batch_size, args.verify_count, args.phase, args.max_records)
    elif args.command == "database":
        result = build_database(args.input, args.run_dir, args.database)
    elif args.command == "cost":
        result = calculate(args.calls, args.rates, args.projected_records); write_report(result, args.out)
    elif args.command == "serve":
        return serve(args.database, args.port)
    elif args.command == "evaluate":
        result = evaluate_golden(args.golden, args.predictions, args.out)
    elif args.command == "export":
        result = export_grading(args.input, args.run_dir, args.grading_dir)
    else:
        raise AssertionError(args.command)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
