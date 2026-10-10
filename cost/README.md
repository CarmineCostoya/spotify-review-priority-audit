# Cost and runtime evidence

Offline replay is the safe default and never calls a model:

```bash
PYTHONPATH=src python3 -m spotify_audit.cli cost \
  --calls cost/pilot_calls.jsonl --rates cost/rates.csv \
  --out cost/report.md --projected-records 100000
```

The paid cold pilot is a separate, explicit command. It requires a local `.env` or exported key and an
affirmative flag:

```bash
OPENAI_API_KEY=... PYTHONPATH=src python3 -m spotify_audit.cli run \
  --input course_material/cost_100.csv --run-dir cost/cold-run \
  --provider openai --batch-size 10 --verify-count 10 --allow-paid
```

Do not claim measured API cost until `pilot_calls.jsonl` contains real provider usage. Copy validated cold-run
records and calls to `cost/pilot_records.jsonl` and `cost/pilot_calls.jsonl`, then rerun the same input without
clearing the saved run directory to demonstrate zero new enrichment calls.

