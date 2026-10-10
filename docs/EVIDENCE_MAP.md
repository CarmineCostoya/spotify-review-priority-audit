# Rubric evidence map

This map separates verified development evidence from work that still requires human labels, provider
credentials, or external publication.

## Deliverable quality

| Criterion | Evidence | Status |
|---|---|---|
| Accessible code and setup | `README.md`, `pyproject.toml`, `Makefile`, `.env.example` | Ready locally |
| Architecture, schema, provenance | `docs/LABELS.md`, `prompts/`, `src/spotify_audit/contract.py` | Ready |
| Correct calculations and source evidence | `grading/membership.csv`, `grading/ranking.csv`, `grading/claims.csv` | Mechanical development check passes |
| Recommendation, alternatives, limitations | `outputs/runs/dev-100000-resume/memo.md` | Development-only; replace after model run |

## Testing and evaluation

| Criterion | Evidence | Status |
|---|---|---|
| Golden 50 and error analysis | `evals/golden_50_to_label.csv`, evaluator command | Human labels required |
| Independent verification and system tests | `verification.jsonl`, `verification_report.json`, `tests/` | Framework ready; real model outcome pending |
| Cost/runtime and controls | `cost/`, guarded paid command, resume tests | Real cold/warm pilot pending API key |

## Working result

| Criterion | Evidence | Status |
|---|---|---|
| 100,000-review coverage | `grading/`, `outputs/self-check-100000.json` | Passes checker in development mode |
| Runnable staged program and resume | `src/spotify_audit/`, checkpoints in `grading/` | Ready |
| Ranking and deployed dashboard | offline ranking, SQLite API, `dashboard/`, `dashboard-site/` | Local verified; external publishing awaiting approval |

## Important warning

The current 100,000-record export uses `local-heuristic-v1` to validate software and accounting. It is not
the final model result and must not be represented as such. The official submission must replace these records
with the evaluated provider run and its actual token/cost evidence.

