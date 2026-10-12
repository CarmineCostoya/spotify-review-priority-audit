# Spotify Review Priority Audit

An auditable, staged pipeline that turns 100,000 historical Spotify app reviews into a traceable product
recommendation. The professor's in-class scope update is applied as **100,000 successfully classified nonempty
reviews**.

## Final result

**Recommendation:** prioritize `PLAYBACK-GENERAL` - failures that prevent reliable starting, loading, selecting,
or continuing music. It ranks first with 6,887 complaint/cancellation reviews, mean severity 3.195876, and a
priority score of 22,010. See the [final decision memo](outputs/runs/final-100000/memo.md) and
[checked numerical claims](grading/claims.csv).

| Result | Official value |
|---|---:|
| Selected source reviews | 100,000 |
| Valid completed classifications | 100,000 |
| Quarantined or unresolved | 0 |
| Unique reviews model-enriched | 75,894 |
| Exact-text cache reuses | 24,106 |
| Independent verification sample | 1,000 |
| Reviews with any topic/intent/severity disagreement | 135 (13.5%) |
| Golden 50 topic / intent / exact severity agreement | 94% / 92% / 86% |
| Logged successful-call API cost | $3.523864 |
| Deterministic checker | `pass`, no issues |

The official [run summary](outputs/runs/final-100000/run_summary.json),
[verification report](outputs/runs/final-100000/verification_report.json),
[cost report](outputs/runs/final-100000/cost_report.md), and
[self-check result](outputs/self-check-final-100000.json) can be inspected without an API key.

### Corrected baseline ranking

Priority is `complaint_count x mean_severity`, exactly equal to `severity_sum`. Complaint and cancellation
reviews are counted once in one deterministic issue group. Ties sort by ascending issue ID.

| Rank | Issue | Complaint/cancellation reviews | Mean severity | Priority score |
|---:|---|---:|---:|---:|
| 1 | `PLAYBACK-GENERAL` | 6,887 | 3.195876 | 22,010 |
| 2 | `USABILITY-GENERAL` | 4,783 | 2.604432 | 12,457 |
| 3 | `USABILITY-ADS` | 4,494 | 2.158656 | 9,701 |

The full [ranking](grading/ranking.csv), [issue membership](grading/membership.csv), and
[claim table](grading/claims.csv) are saved. During final memo review, a word-boundary defect was found in the
advertising subgroup: `ad` had matched inside words such as “load,” “made,” and “add.” Correct whole-word
matching removed 2,461 false advertising matches. The downstream membership, ranking, claims, grading export,
and database were regenerated from saved classifications without new model calls. A regression test now covers
this case.

## Submission access

- **Public GitHub repository:** https://github.com/CarmineCostoya/spotify-review-priority-audit
- **Live database-backed dashboard:** https://spotify-review-priority-audit.ccostoyaruiz.chatgpt.site
- **Interruption/resume recording:** [silent captioned demonstration](https://drive.google.com/file/d/1FULOF_XK3WMUz5DyDVkS04E88fmp14Bi/view?usp=drive_link)
- **Local dashboard:** `http://127.0.0.1:8000` after following the commands below

The live dashboard exposes the official aggregate metrics, all 21 ranked issues, the grounded recommendation,
and eight representative source-review evidence records through a deployed D1 database. The complete
100,000-review SQLite database is reproducible locally from the saved grading records and the course dataset.

## Dataset and scope

The source is BwandoWando's [3.4 Million Spotify Google Store Reviews](https://www.kaggle.com/datasets/bwandowando/3-4-million-spotify-google-store-reviews),
version 2, published as CC0. The course extract covers May 2022 through November 2023.

- Supplied full extract: 660,622 rows, SHA-256
  `1fc85de68a304dd8978b537cfa58793d5f41cbaf417fa32cb53899f83a2fcef6`
- Verified full-file profile: 660,609 nonempty texts, 13 empty texts, 159,701 missing app versions, and no repeated
  review IDs
- Final analysis scope: the first 100,000 nonempty rows in source order, following the professor's updated
  minimum requirement
- Selection details: [selection manifest](data/analysis_100000.selection.json)
- Complete source metadata and checksums: [course manifest](course_material/manifest.json)

The 97.4 MB source CSV and selected analysis CSV remain local and are intentionally ignored by Git. Place the
course-provided files in `course_material/` before reproducing ingestion or selection.

## Architecture and responsibilities

```text
full CSV
   |
   v
prepare/code --> exact-text cache --> enrich/model --> verify/independent model task
                                           |                    |
                                           +---- validated JSON-+
                                                        |
                                                        v
group/code --> rank/code --> checked claims --> memo/bounded evidence
     |              |                              |
     +------ saved handoffs and checkpoints -------+
                            |
                            v
                         SQLite --> Python backend --> dashboard

Failures -> bounded retry -> quarantine if unresolved
Interruption -> checkpoint -> resume only pending/failed IDs
```

| Stage | Owner | Input | Saved output and control |
|---|---|---|---|
| Prepare | Code | Full CSV | Profile, stable IDs/hashes, 100,000-row selection, duplicate-text queue |
| Enrich | GPT-6 Luna, effort `none` | Original review text only | Fixed topic/intent/severity schema, exact quote, maximum 25 reviews per final-run request |
| Verify | Separate `verify` invocation of the same model/rubric | Random source-text sample without first prediction | Independent predictions and code-generated disagreements |
| Group | Code | Completed complaint/cancellation records | One stable issue membership per contributing review; no model call |
| Rank | Code | Saved records and membership | Counts, severity sums, six-decimal means, stable order; no model call |
| Recommend | Deterministic bounded template plus human review | Saved aggregates and selected evidence | Checked memo claims, alternatives, limitations |
| Serve | SQLite + Python backend | Saved reviews, membership, ranking | Metrics, rankings, recommendation, and review-level evidence for the dashboard |

Code owns accounting, source hashes, schema checks, exact-quote validation, cache provenance, arithmetic,
checkpoints, retry state, and persistence. The model is used only for bounded language classification. Human
Golden 50 answers were never model inputs. See [label definitions](docs/LABELS.md),
[enricher prompt](prompts/enricher_v2.md), [verifier role](prompts/verifier_v1.md), and the
[pipeline implementation](src/spotify_audit/pipeline.py).

## Traceability examples

### One review through the pipeline

Review `e617fefb-775e-44b2-afe0-d5a97fad6fa6` reports being unable to play across devices.

1. The source row is preserved and hashed as
   `df96fa2342558fa2a550a001f45828c5e1d5d3c791c7ea6b7c135d02b730e213`.
2. Enrichment assigns `topic=playback`, `intent=complaint`, and `severity=3`, with an exact source quote.
3. The independent verifier agrees on topic, intent, and severity.
4. Deterministic grouping places the review in `PLAYBACK-GENERAL`.
5. That membership contributes 3 to the issue's severity sum of 22,010.
6. The issue ranks first and supports `CLAIM-001` through `CLAIM-004` in the final memo.

The source classification is in [records.jsonl](grading/records.jsonl), its membership is in
[membership.csv](grading/membership.csv), and the aggregate is in [ranking.csv](grading/ranking.csv).

### Ambiguous/disagreement example

For review `557e0726-c979-4606-9fb5-fa5dae16e8b9`, the enricher chose `catalog` while the blind verifier chose
`usability`; both agreed it was praise with severity 1. The disagreement remains visible in the
[verification report](outputs/runs/final-100000/verification_report.json) rather than being silently replaced.
It does not enter the complaint ranking.

## Evaluation and safeguards

### Golden 50

The completed human-label file is separate from the model inputs. V2 improved over V1 after five human labels
were adjudicated strictly against the published rubric.

| Metric | V1 | V2 final |
|---|---:|---:|
| Topic agreement | 92% | 94% |
| Intent agreement | 90% | 92% |
| Exact severity agreement | 76% | 86% |
| Severity mean absolute error | 0.28 | 0.14 |
| Rows with any mismatch | 17 | 11 |

Evidence: [Golden 50 labels](evals/golden_50_to_label.csv),
[V2 results](evals/golden_results_v2.json), and [error analysis](evals/golden_error_analysis.md).
The 50 cases are a diagnostic sample, not a population-accuracy estimate.

### Independent verification

The verifier independently relabeled 1,000 randomly selected completed reviews. It disagreed on at least one
ranked field for 135 reviews: 84 topic, 43 intent, and 28 severity differences; a review may differ on multiple
fields. The 86.5% full-field agreement is disclosed rather than used to overwrite the original run. In addition,
11,378 completed records have `needs_review=true`; they remain valid completed records but are the first candidates
for further human adjudication.

### System checks

Eight automated tests cover source hashing, evidence-quote membership, ranking tie-breaks, paid-provider lockout,
resume without duplicate enrichment, retry of classification failures, bounded parallel workers, and the
advertising word-boundary regression. Synthetic cases for malformed/injected text and other awkward paths are
saved in [system cases](evals/system_cases.jsonl). Run them with:

```bash
make test
```

## Cost, retries, and recovery

Paid execution requires both an API key and the explicit `--allow-paid` flag. Importing, inspecting, reranking,
building the database, serving the dashboard, running tests, and replaying cost evidence make no paid calls.

The required cold 100-review pilot used one worker and completed all 100 reviews in 73.974 seconds. It logged 10
enrichment calls plus one verifier call and cost $0.005315 at the editable rates. The warm run reused all 100
enrichments, made zero new enrichment calls, and made one fresh verifier call in 6.964 seconds. See the
[pilot report](cost/report.md), [warm evidence](cost/warm_resume_evidence.json),
[saved calls](cost/pilot_calls.jsonl), and [editable rates](cost/rates.csv).

The official run logged 3,727 successful measured API calls, $3.523864 in successful-call usage, and 24,106
exact-text cache reuses. Failed responses did not expose usage, so the provider invoice can be slightly higher.
The 614.162-second duration in the final run summary covers the final recovery invocation, not the complete
interrupted run's wall-clock duration.

The official run was interrupted after 9,309 completed IDs, then resumed with five bounded workers. It reached
93,379 completed records in the main resumed pass; failed batches were recovered with batch sizes 10 and 1 until
all 100,000 were complete. The [recovery narrative](outputs/runs/final-100000/recovery.md),
[before checkpoint](grading/checkpoint_before.json), [after checkpoint](grading/checkpoint_after.json), and
[call log](grading/calls.jsonl) preserve this evidence.

Replay cost arithmetic offline:

```bash
PYTHONPATH=src python3 -m spotify_audit.cli cost \
  --calls cost/pilot_calls.jsonl --rates cost/rates.csv \
  --out cost/report.md --projected-records 100000
```

## Setup

Requirements: Python 3.11 or newer. The runtime pipeline has no third-party Python dependencies.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
cp .env.example .env
```

Add an OpenAI API key to `.env` only if making paid calls. `.env` and `.env.*` are ignored; only the blank
`.env.example` belongs in Git. Never put a real key in source files, logs, screenshots, browser code, or commits.

## Safe offline reproduction

Profile the supplied full file and regenerate the deterministic 100,000-row selection:

```bash
make test
make profile
make select
```

Regenerate issue membership, numerical claims, and ranking from the saved official classifications without any
model calls:

```bash
PYTHONPATH=src python3 -m spotify_audit.cli rerank \
  --input data/analysis_100000.csv \
  --run-dir outputs/runs/final-100000
```

Run the professor's zero-API checker:

```bash
python3 course_material/check_submission.py profile \
  --full course_material/spotify_reviews_18months.csv \
  --out grading/ingestion.json
python3 course_material/check_submission.py reference \
  --full course_material/spotify_reviews_18months.csv \
  --analysis data/analysis_100000.csv \
  --out outputs/final-reference-100000.json
python3 course_material/check_submission.py check \
  --reference outputs/final-reference-100000.json \
  --submission grading \
  --out outputs/self-check-final-100000.json
```

The saved result is `status=pass`, 100,000 valid completed records, zero missing or quarantined, 24,106 valid
cache reuses, and no mechanical issues.

## Explicit paid commands

Paid calls are never the default. The 100-review cold pilot command is:

```bash
OPENAI_API_KEY=... PYTHONPATH=src python3 -m spotify_audit.cli run \
  --input course_material/cost_100.csv --run-dir cost/cold-run \
  --provider openai --batch-size 10 --verify-count 10 --workers 1 --allow-paid
```

The official run command was:

```bash
OPENAI_API_KEY=... PYTHONPATH=src python3 -m spotify_audit.cli run \
  --input data/analysis_100000.csv --run-dir outputs/runs/final-100000 \
  --provider openai --batch-size 25 --verify-count 1000 --workers 5 --allow-paid
```

Running the same command against the same directory resumes from saved records instead of paying to reclassify
valid completed IDs under the unchanged configuration.

## Database, backend, and dashboard

Build SQLite from the saved run:

```bash
PYTHONPATH=src python3 -m spotify_audit.cli database \
  --input data/analysis_100000.csv \
  --run-dir outputs/runs/final-100000 \
  --database outputs/spotify_audit.db
```

Start the local backend and dashboard:

```bash
make serve
```

Open `http://127.0.0.1:8000`. The backend reads SQLite rather than loading analysis constants into the browser.
The dashboard requests overall metrics, the full ranking, the grounded recommendation, and issue-level review
evidence from `/api/metrics`, `/api/issues`, and `/api/issues/{issue_id}`. Implementation:
[database builder](src/spotify_audit/database.py), [backend](src/spotify_audit/server.py), and
[dashboard](dashboard/).

## Repository layout

```text
src/spotify_audit/       pipeline, validation, cost, database, API, CLI
prompts/                  versioned role instructions
docs/                     labels and rubric evidence map
evals/                    Golden 50, comparisons, error analysis, system cases
cost/                     measured pilot usage, rates, replay report
grading/                  standardized 100,000-review checker export
outputs/runs/final-100000 compact official reports and memo
dashboard/                local database-backed user interface
dashboard-site/           deployment build scaffold
tests/                    deterministic regression tests
```

## Rubric-to-evidence map

| Rubric criterion | Primary evidence | Status |
|---|---|---|
| Accessible code, setup, and artifacts | This README, [package config](pyproject.toml), [CLI](src/spotify_audit/cli.py), [grading export](grading/) | Publicly available |
| Architecture, schema, and provenance | Diagram above, [labels](docs/LABELS.md), [contract](src/spotify_audit/contract.py), [prompts](prompts/) | Complete |
| Correct calculations and source evidence | [membership](grading/membership.csv), [ranking](grading/ranking.csv), [claims](grading/claims.csv), [checker](outputs/self-check-final-100000.json) | Checker passes |
| Recommendation, alternatives, limitations | [Final memo](outputs/runs/final-100000/memo.md) | Complete; human-reviewed |
| Golden labels and error analysis | [Golden 50](evals/golden_50_to_label.csv), [V2 results](evals/golden_results_v2.json), [analysis](evals/golden_error_analysis.md) | Complete |
| Independent verification and system tests | [Verification report](outputs/runs/final-100000/verification_report.json), [tests](tests/), [system cases](evals/system_cases.jsonl), [resume recording](https://drive.google.com/file/d/1FULOF_XK3WMUz5DyDVkS04E88fmp14Bi/view?usp=drive_link) | Complete; 135/1,000 disclosed |
| Cost/runtime and controls | [Pilot report](cost/report.md), [rates](cost/rates.csv), [official cost](outputs/runs/final-100000/cost_report.md), [recovery](outputs/runs/final-100000/recovery.md) | Complete locally |
| Full ingestion and classification coverage | [Ingestion](grading/ingestion.json), [records](grading/records.jsonl), [checker](outputs/self-check-final-100000.json) | 100,000/100,000 valid |
| Runnable stages, bounded calls, saved handoffs, resume | [Pipeline](src/spotify_audit/pipeline.py), [calls](grading/calls.jsonl), [checkpoints](grading/checkpoint_before.json) | Complete |
| Reproducible ranking and usable deployed dashboard | `rerank` command, SQLite backend, [live dashboard](https://spotify-review-priority-audit.ccostoyaruiz.chatgpt.site) | Published |

See the expanded [evidence map](docs/EVIDENCE_MAP.md) and [project status](PROJECT_STATUS.md).

## Limitations

- App-store reviewers are self-selected; counts do not estimate prevalence among all Spotify customers.
- Reviews are historical and contain no revenue, plan tier, confirmed cancellation, retention outcome, or complete
  customer population. Cancellation language is intent, not observed churn.
- Model classifications remain uncertain: 13.5% of the independent sample had at least one ranked-field
  disagreement, and 11,378 records were flagged for review.
- Exact quote membership proves provenance, not that every quote perfectly supports its label.
- Deterministic keyword subgroups can miss synonyms and assign only one issue to a multi-issue review.
- The measured cost excludes unknown usage from failed provider responses. The complete interrupted run did not
  retain one continuous wall-clock timer.
- The hosted dashboard intentionally contains aggregate outputs and a small representative evidence subset;
  the full 100,000-review database is built locally to avoid republishing the complete course dataset.
