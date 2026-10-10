# Evaluation workflow

`golden_50_to_label.csv` is intentionally blank. The student must label it before model evaluation; assistant-
generated labels are not human labels and must not be represented as such.

After the real provider predicts these 50 reviews into a separate run directory:

```bash
PYTHONPATH=src python3 -m spotify_audit.cli evaluate \
  --golden evals/golden_50_to_label.csv \
  --predictions outputs/runs/golden-model/records.jsonl \
  --out evals/golden_results.json
```

Do not use the expected columns as model inputs. Save ambiguous cases and concrete disagreements.

