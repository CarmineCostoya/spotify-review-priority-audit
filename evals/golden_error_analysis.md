# Golden 50 error analysis

## Initial V1 results before adjudication

The `gpt-6-luna+effort-none+labels-v1+record-v1` run completed all 50 reviews with no quarantined records.
These figures use the original human labels, before the five rubric-inconsistent labels listed below were corrected.

| Metric | All 50 | Clear 40 | Ambiguous 10 |
|---|---:|---:|---:|
| Topic agreement | 92.0% | 97.5% | 70.0% |
| Intent agreement | 86.0% | 95.0% | 50.0% |
| Exact severity agreement | 70.0% | 72.5% | 60.0% |
| Severity mean absolute error | 0.40 | 0.375 | 0.50 |

The model made four topic errors, seven intent errors, and fifteen severity errors. Severity errors were balanced:
eight predictions were lower than the golden label and seven were higher.

## Main error patterns

1. **Paid-plan language pulled topic toward billing.** Review 10 praised Premium having no ads; the golden topic
   was usability, while the model selected billing. Version 2 states that a paid-plan name alone is not billing.
2. **Problem reports containing requests were inconsistently labeled.** Reviews 11 and 12 report failures and ask
   for a fix. The shared precedence rule says complaint outranks request, so these golden labels should be
   adjudicated before using them to tune the model.
3. **Tone was confused with functional severity in the golden labels.** Reviews 6, 13, and 20 contain generic
   criticism but were labeled severity 4. The published rubric maps generic criticism without functional loss to
   severity 2. The model predicted 2 for all three. These are golden-label adjudication candidates, not prompt
   failures.
4. **Restricted functions were sometimes promoted to a full core-task block.** Reviews 29, 38, and 45 still have
   some usable path, so version 2 gives explicit severity-3 examples for song controls, lyrics, and offline-only loss.
5. **Strong wording or safety language inflated severity.** Review 33 was predicted severity 5 even though the
   rubric reserves 5 for explicit financial, privacy, or data harm. Version 2 makes that boundary explicit.
6. **Ambiguous or multilingual fragments drove most categorical errors.** Reviews 17, 21, 27, 28, 34, and 48
   require translation or interpretation. These should retain `needs_review=true`; they are not reliable prompt-
   tuning examples without human adjudication.

## Concrete disagreements to adjudicate

| Review | Field | Golden | Prediction | Recommended action |
|---:|---|---|---|---|
| 1 | Severity | 4 | 3 | Recheck whether unavailable catalog content blocks a core task or is restricted content. |
| 6 | Severity | 4 | 2 | Change golden to 2 unless a functional loss is present outside the text. |
| 11 | Intent | request | complaint | Apply precedence: a reported playback failure plus “fix” is complaint. |
| 12 | Intent | request | complaint | Apply precedence and decide whether the resolved update changes severity. |
| 13 | Severity | 4 | 2 | Change golden to 2 unless “bad work” is interpreted as a clear core-task block. |
| 17 | Topic/intent | catalog/praise | other/unclear | Keep needs-review flag and obtain a confident translation before adjudication. |
| 20 | Severity | 4 | 2 | Change golden to 2; anger alone does not raise severity. |
| 21 | Intent | cancellation | unclear | Confirm whether “boycotting” counts as explicit cancellation. Version 2 treats it as cancellation. |
| 24 | Severity | 3 | 1 | Confirm translation; repeated ads indicate degraded use if the translation is correct. |
| 33 | Severity | 3 | 5 | Keep 3 under the current rubric; severity 5 is limited to financial/privacy/data harm. |
| 48 | Topic/intent | other/complaint | usability/request | Keep needs-review flag; the text does not name a specific failed feature. |

## Version 2 changes

- Clarified that Premium mentions do not automatically mean billing.
- Added explicit cancellation terms, including boycott.
- Distinguished a complaint that asks for a fix from a pure feature request.
- Added concrete severity boundaries for generic criticism, restricted features, core-task blocks, and severity 5.
- Required `needs_review=true` for uncertain translations and unresolved fragments.
- Directed the model to use the full review when an exact shorter evidence quote is uncertain.

The measured V2 run used a fresh run directory because the label configuration changed from `labels-v1` to
`labels-v2`. This prevented cached V1 records from being counted as V2 predictions.

## Adjudication completed

The following corrections were applied to the Golden 50 using the assignment rubric:

- Reviews 6, 13, and 20: severity changed from 4 to 2 because the text contains criticism but no stated
  functional loss.
- Reviews 11 and 12: intent changed from `request` to `complaint` because each review reports an existing
  failure; the request to fix it is secondary.

All 50 rows remain present. Entity values are valid JSON lists, and every evidence quote is an exact substring
of its review text.

## Fair V1-to-V2 comparison after adjudication

Both versions below were evaluated against the same corrected Golden 50.

| Metric | V1 | V2 | Change |
|---|---:|---:|---:|
| Topic agreement | 92.0% | 94.0% | +2 percentage points |
| Intent agreement | 90.0% | 92.0% | +2 percentage points |
| Exact severity agreement | 76.0% | 86.0% | +10 percentage points |
| Severity mean absolute error | 0.28 | 0.14 | 50% lower |
| Missing predictions | 0 | 0 | No change |
| Rows with any mismatch | 17 | 11 | 6 fewer |
| Verifier disagreements in 10-review sample | 3 | 1 | 2 fewer |

V2 improved every measured quality metric. Its largest gain was severity, which was the main weakness in V1.
The V2 run completed all 50 reviews with zero quarantined records and cost approximately $0.002627 using the
assignment-provided rates in `cost/rates.csv`.
