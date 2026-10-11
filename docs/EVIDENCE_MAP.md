# Rubric evidence map

This map identifies the verified official-run and publication evidence.

## Deliverable quality

| Criterion | Evidence | Status |
|---|---|---|
| Accessible code and setup | `README.md`, `pyproject.toml`, `Makefile`, `.env.example` | Published on GitHub |
| Architecture, schema, provenance | `docs/LABELS.md`, `prompts/`, `src/spotify_audit/contract.py` | Ready |
| Correct calculations and source evidence | `grading/membership.csv`, `grading/ranking.csv`, `grading/claims.csv` | Official checker passes |
| Recommendation, alternatives, limitations | `outputs/runs/final-100000/memo.md` | Complete and human-reviewed |

## Testing and evaluation

| Criterion | Evidence | Status |
|---|---|---|
| Golden 50 and error analysis | `evals/golden_50_to_label.csv`, `evals/golden_error_analysis.md`, V1/V2 result files | Complete; V2 improved every metric |
| Independent verification and system tests | `outputs/runs/final-100000/verification_report.json`, `tests/` | Official: 135/1,000 disagreements; 8/8 tests pass |
| Cost/runtime and controls | `outputs/runs/final-100000/cost_report.md`, `recovery.md` | Official logged successful-call cost: $3.523864 |

## Working result

| Criterion | Evidence | Status |
|---|---|---|
| 100,000-review coverage | `grading/`, `outputs/self-check-final-100000.json` | Official checker passes; 100,000/100,000 valid |
| Runnable staged program and resume | `src/spotify_audit/`, checkpoints in `grading/`, official `recovery.md` | Verified on official run |
| Ranking and deployed dashboard | offline ranking, SQLite API, `dashboard/`, `dashboard-site/` | Published and publicly accessible |

## Remaining warning

The checker validates artifact consistency; it does not replace human review of recommendation quality or the
135 verification disagreements. The hosted D1 database contains the aggregate outputs and eight representative
evidence reviews; the complete 100,000-review SQLite database is rebuilt locally from the saved artifacts.
