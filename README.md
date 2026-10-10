# Spotify Review Priority Audit

An auditable multi-role pipeline that converts Spotify app reviews into a traceable product recommendation.
The professor's in-class scope update is treated as **100,000 successfully classified nonempty reviews**.

## Current status

The repository contains a working offline development pipeline, exact grading-contract hashes and validation,
resume/cache behavior, independent verification, deterministic grouping/ranking, a SQLite-backed API, dashboard,
tests, and an offline cost calculator. The downloaded course data stays local and is ignored by Git.

The real paid 100-review cold/warm pilot and official 100,000-review model run are intentionally not fabricated:
they require a configured provider key and explicit `--allow-paid`. Development heuristic outputs are always
labeled `local-heuristic-v1` and must not be presented as measured model results.

## Architecture

```text
CSV -> prepare/code -> enrich/model -> verify/separate role -> group/code
    -> rank/code -> recommend/bounded evidence -> SQLite -> backend -> dashboard
          |             |                    |
          +-- checkpoints, call logs, validated saved handoffs --+
```

Code owns IDs, hashes, status accounting, validation, caching, membership, arithmetic, budgets, and persistence.
Models are limited to bounded language decisions and never receive human golden labels.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
cp .env.example .env
```

Place the supplied files in `course_material/`. Do not commit the 97.4 MB raw CSV.

## Safe offline workflow

```bash
make test
make profile
make select
make demo
PYTHONPATH=src python3 -m spotify_audit.cli database \
  --input course_material/cost_100.csv --run-dir outputs/runs/dev-100 \
  --database outputs/spotify_audit.db
make serve
```

Open `http://127.0.0.1:8000`.

## Explicit paid pilot

Paid calls cannot occur merely by importing or opening this project. They require both a key and `--allow-paid`:

```bash
OPENAI_API_KEY=... PYTHONPATH=src python3 -m spotify_audit.cli run \
  --input course_material/cost_100.csv --run-dir cost/cold-run \
  --provider openai --batch-size 10 --verify-count 10 --allow-paid
```

Run the same command again against the same directory for the warm/resume demonstration. Existing completed IDs
are loaded before dispatch. See `cost/README.md` for offline replay.

## Final 100,000 workflow

After the pilot, golden evaluation, and 500/10,000 checkpoints have been reviewed:

```bash
make select
OPENAI_API_KEY=... PYTHONPATH=src python3 -m spotify_audit.cli run \
  --input data/analysis_100000.csv --run-dir outputs/runs/final-100000 \
  --provider openai --batch-size 25 --verify-count 1000 --allow-paid
```

Do not run this until the measured projection fits the declared budget. The exact selection method is saved next
to `analysis_100000.csv`.

## Limitations

These historical reviews are self-selected. They do not contain revenue, confirmed cancellations, plan tiers,
or the complete customer population. Results cannot establish causal retention improvements. Development
heuristics are scaffolding, not final model evidence.

