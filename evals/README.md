# Evaluation workflow

`golden_50_to_label.csv` contains the completed and rubric-adjudicated human labels used for the final
evaluation. The expected columns were never supplied to the model. `golden_results_v1_adjudicated.json` and
`golden_results_v2.json` contain the comparable model results, and `golden_error_analysis.md` documents the
disagreements and prompt changes.

To evaluate a saved prediction file without making model calls:

```bash
PYTHONPATH=src python3 -m spotify_audit.cli evaluate \
  --golden evals/golden_50_to_label.csv \
  --predictions outputs/runs/golden-model/records.jsonl \
  --out evals/golden_results.json
```

Do not use the expected columns as model inputs. Save ambiguous cases and concrete disagreements.
