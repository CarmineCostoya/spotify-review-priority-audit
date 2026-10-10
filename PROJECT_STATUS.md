# Project status

## Completed and verified

- Downloaded and checksum-verified the official course dataset.
- Profiled all 660,622 source rows: 660,609 nonempty, 13 empty, 159,701 missing app versions,
  484,189 distinct nonempty texts, and no repeated review IDs.
- Created a deterministic 100,000-nonempty-review analysis file.
- Implemented prepare, enrich, verify, group, rank, recommend, database, API, dashboard, cost replay,
  golden evaluation, and grading-export commands.
- Implemented exact source-row hashing, bounded requests, schema validation, exact-quote checks,
  direct duplicate-text cache provenance, atomic saved outputs, and interruption/resume checkpoints.
- Ran offline development checkpoints at 100, 500, 10,000, and 100,000 reviews.
- Loaded 100,000 development records into SQLite and verified API endpoints.
- Ran the supplied checker against the 100,000-record development export: `status=pass`, full coverage,
  24,106 valid exact-text cache reuses, and no mechanical issues.
- Prepared and validated the Sites dashboard build.

## Required before submission

1. The student must hand-label `evals/golden_50_to_label.csv`.
2. Configure a model-provider key locally and run the real 100-review cold/warm pilot.
3. Review golden results and revise/freeze prompts using development data only.
4. Run real 500 and 10,000 checkpoints, refresh the cost projection, and approve the budget.
5. Run the real 100,000-review model pipeline and replace development exports.
6. Inspect disagreements, ambiguous outputs, and top issue examples; finalize the memo.
7. Publish the GitHub repository and a database-backed dashboard, then test both while signed out.
8. Record the interruption/resume demonstration and link it in the README.

## Current blockers

- No `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, or `TYPESAFE_API_KEY` is configured.
- GitHub access is not connected and the `gh` CLI is unavailable.
- External Sites publication needs explicit approval because it transmits dataset-derived metrics and
  recommendations to the hosted repository.

