# Product priority memo

## Decision

Spotify should make **general playback reliability** the next-quarter priority. In this analysis,
`PLAYBACK-GENERAL` ranks first with **6,887 complaint or cancellation reviews**, **mean severity 3.195876**,
and a **priority score of 22,010** (`CLAIM-001`, `CLAIM-003`, `CLAIM-004`). The score is the issue's severity
sum, equivalently complaint count multiplied by mean severity; it is a transparent prioritization baseline,
not an estimate of revenue or churn.

The recurring customer problem is basic listening reliability: the app or song does not load, Spotify reports
no connection despite available service, the requested track is replaced by another track, or playback is
otherwise unusable. These reports affect the product's core job - letting a user start and continue listening -
and combine high frequency with an average impact above severity 3 (degraded or restricted function).

## Evidence from the 100,000-review run

| Rank | Issue | Complaint/cancellation reviews | Mean severity | Priority score | Saved claims |
|---:|---|---:|---:|---:|---|
| 1 | `PLAYBACK-GENERAL` | 6,887 | 3.195876 | 22,010 | `CLAIM-001` to `CLAIM-004` |
| 2 | `USABILITY-GENERAL` | 4,783 | 2.604432 | 12,457 | `CLAIM-005` to `CLAIM-008` |
| 3 | `USABILITY-ADS` | 4,494 | 2.158656 | 9,701 | `CLAIM-009` to `CLAIM-012` |

The underlying severity sums are 22,010, 12,457, and 9,701 respectively (`CLAIM-002`, `CLAIM-006`,
`CLAIM-010`). Each contributing review is linked to exactly one saved issue membership, and the complete
ranking can be regenerated from the saved records without a model call.

Representative `PLAYBACK-GENERAL` evidence:

- `b3da207e-888d-40bd-bd5d-11f376f5eeda` reports that selecting a favorite song plays another song
  (complaint, severity 3).
- `6344f653-1a48-44df-a9f7-d8a28bceee75` reports no music and a false no-internet message despite an
  available connection (complaint, severity 3).
- `1d2804a8-3d89-4609-afeb-a369266816df` reports being unable to play any selected song
  (complaint, severity 4).
- `3d9c548f-1c89-44f2-bc65-9fbde01fa6ab` reports that the app remains stuck on its logo screen even after
  a reinstall (complaint, severity 4).

These examples illustrate the issue; the recommendation rests on all 6,887 saved memberships, not on the
selected quotations alone.

## Recommended next-quarter response

Create a focused playback-reliability program covering four observed failure modes:

1. **Playback start:** instrument and reduce failures between tapping a track and first audio.
2. **App and session readiness:** investigate logo-screen, loading, and false connectivity failures.
3. **Selection correctness:** test cases where Spotify plays a different track or forces unexpected shuffle.
4. **Regression control:** segment failures by app version and device where those source values are available,
   then gate releases on playback-start success, crash-free listening sessions, and time-to-first-audio.

Before committing to a specific engineering fix, product and engineering teams should inspect a stratified
sample of high-severity memberships and connect the review themes to internal telemetry. The review data shows
where customers report pain; it does not identify a single technical root cause.

## Alternatives considered

### General usability

`USABILITY-GENERAL` ranks second with **4,783 complaint or cancellation reviews**, **mean severity 2.604432**,
and **priority score 12,457** (`CLAIM-005`, `CLAIM-007`, `CLAIM-008`). Examples include broken shuffle or
navigation controls (`da6377bb-76c1-4c6f-a64a-4728adbc275a`) and an unexpected playback-control layout change
(`faf05e24-a8eb-4726-ad2f-3c2b989bfbd2`). This is a meaningful secondary workstream, but its lower baseline
score and lower mean severity make it less urgent than core playback reliability.

### Advertising experience

`USABILITY-ADS` ranks third with **4,494 complaint or cancellation reviews**, **mean severity 2.158656**, and
**priority score 9,701** (`CLAIM-009`, `CLAIM-011`, `CLAIM-012`). Examples report repeated ads between songs
(`cd61e48a-5606-4615-8811-d0e27e6b0036`) and an ad-to-music balance that feels excessive
(`b78cef3b-2abc-4c6e-b54d-b61bc4668eed`). Advertising remains important, but many reports describe annoyance
rather than complete functional loss, which is reflected in the lower mean severity.

## Confidence and quality checks

- The official run accounts for **100,000 source reviews**, with **100,000 completed classifications** and
  **zero quarantined records**. Exact-text caching reused 24,106 classifications while preserving every source
  review ID and direct cache provenance.
- The human-labeled Golden 50 evaluation reached 94% topic agreement, 92% intent agreement, 86% exact severity
  agreement, and severity mean absolute error 0.14 after rubric-based adjudication.
- A separate verifier independently relabeled 1,000 reviews without seeing the first prediction. It disagreed on
  at least one ranked field for 135 reviews, giving **86.5% full-field agreement**. The disagreements included
  84 topic, 43 intent, and 28 severity differences; one review can differ on multiple fields.
- The model marked 11,378 completed reviews as `needs_review=true`. These remain included because they passed
  the schema and evidence checks, but they are a useful priority set for further human review.
- The supplied deterministic checker returns `pass`: all 100,000 source IDs and hashes reconcile, all evidence
  quotes are source substrings, the ranking recomputes, and the numerical claims match the saved aggregates.

During final memo review, a deterministic grouping defect was found and corrected: the original rule treated
`ad` as an unrestricted substring, so words such as "load," "made," and "add" could enter the advertising group.
Whole-word matching removed 2,461 false substring matches. Membership, ranking, claims, grading export, and the
database were then regenerated from the already saved classifications without paid model calls. This correction
is why the final ranking places `USABILITY-GENERAL` second and `USABILITY-ADS` third.

## Limitations

- App-store reviewers are a self-selected population, so issue counts are not prevalence estimates for all
  Spotify customers.
- The data is historical and contains no revenue, plan-tier, confirmed cancellation, retention, or complete
  customer-population data. Cancellation language is expressed intent, not observed churn.
- Severity is inferred from the text under a fixed rubric. Ratings, anger, and cancellation wording alone do not
  establish high severity, and model/verifier disagreement shows remaining classification uncertainty.
- Exact-text cache reuse avoids duplicate model work but does not reduce the business count: each original review
  ID remains represented.
- Issue membership uses deterministic keyword-based subgroups after model topic classification. It supports a
  reproducible baseline but can miss synonyms or place multi-issue reviews under only one issue.
- There are no unresolved or quarantined records, but `needs_review=true` flags should not be interpreted as fully
  adjudicated labels.
- The measured successful-call cost is $3.523864. Failed provider responses did not expose usage, so the provider
  invoice can be slightly higher. The 614.162-second value in the run summary measures the final recovery
  invocation, not the complete interrupted run's wall-clock duration.

## Traceability

The numerical claims above are listed in `claims.csv`; contributing review IDs are in `membership.csv`; the full
arithmetic and stable ordering are in `ranking.csv`; record-level predictions and exact evidence quotes are in
`records.jsonl`; independent verification is in `verification_report.json`; and execution, cost, and recovery
evidence are in `run_summary.json`, `cost_report.md`, `calls.jsonl`, and `recovery.md`.
