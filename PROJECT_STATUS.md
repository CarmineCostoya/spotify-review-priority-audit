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
- Completed and evaluated the human-labeled Golden 50; the V2 prompt reached 94% topic, 92% intent, and 86%
  exact severity agreement.
- Ran the paid 100-review V2 pilot: 100 completed, zero quarantined, and zero verifier disagreements in the
  10-review sample.
- Demonstrated warm resume behavior with zero new enrichment calls and measured a $5.32 variable-cost
  projection for 100,000 reviews.
- Completed the real 500-review V2 checkpoint with zero quarantines, five disagreements in a 50-review
  verification sample, and $0.021236 measured API cost.
- Completed the real 10,000-review V2 checkpoint with zero quarantines, 14 disagreements in a 100-review
  verification sample, 1,852 exact-text cache reuses, and $0.375971 logged successful-call cost.
- Validated all 10,000 results against their source hashes, schemas, and exact evidence quotes; the updated
  variable-cost projection for 100,000 reviews is $4.61.
- Completed the official 100,000-review V2 model run: 100,000 completed, zero quarantined, 24,106 exact-text
  cache reuses, and 135 disagreements in the independent 1,000-review verification sample.
- Logged $3.523864 of successful-call usage and preserved the interrupted/resumed execution evidence.
- Replaced the development grading export with the official model results. The supplied deterministic checker
  returns `status=pass`, full coverage, and no mechanical issues.
- Validated every official record against its source hash, schema, and exact evidence quote; rebuilt SQLite
  with 100,000 completed reviews and 21 ranked issues; all 8 automated tests pass.
- Corrected an advertising subgroup word-boundary defect found during memo review, reran deterministic grouping
  and ranking without model calls, and updated the final memo and traceable claims.
- Rebuilt the README as the grader entry point with final results, reproducible commands, trace examples,
  evaluation/cost/recovery evidence, limitations, and a complete rubric-to-evidence map.
- Published the repository at `https://github.com/CarmineCostoya/spotify-review-priority-audit` and the
  database-backed dashboard at `https://spotify-review-priority-audit.ccostoyaruiz.chatgpt.site`.

## Required before submission

1. Record the interruption/resume demonstration and link it in the README.

## Current blockers

- No implementation or publication blocker remains.
