# Cost and runtime evidence

The measured V2 pilot completed 100 reviews with zero quarantines. The cold run took 73.97 seconds and cost
$0.005315 using the assignment-provided rates. The resulting variable-cost projection for 100,000 reviews is
$5.32. The warm replay took 6.96 seconds, reused all 100 enrichment records, and made zero new enrichment calls.
Its one model call was the deliberately fresh 10-review verification sample.

The real 500-review checkpoint then completed all 500 source records with zero quarantines. Exact-text caching
reduced the model workload to 437 unique enrichment records. The run cost $0.021236, took 258.06 seconds, and
had five disagreements in its independent 50-review verification sample. Its detailed cost report is saved at
`outputs/runs/model-500/cost_report.md`.

The real 10,000-review checkpoint completed all records with zero quarantines. It reused 1,852 exact-text
matches and made 8,148 unique enrichment classifications. The logged successful calls cost $0.375971 and
produce a $4.61 variable-cost projection for 100,000 reviews. The independent 100-review verification sample
had 14 disagreements. Details are in `outputs/runs/model-10000/`.

The official 100,000-review run completed all records with zero quarantines. It reused 24,106 exact-text
matches and model-enriched 75,894 unique reviews. Its 3,727 successful measured API calls used 6,264,635
uncached input tokens, 1,860 cached input tokens, and 5,794,764 output tokens, for $3.523864 at the supplied
rates. Failed provider responses did not expose usage and are excluded from this measured total, so the
provider invoice can be slightly higher. The independent 1,000-review verification sample had 135
disagreements. Details are in `outputs/runs/final-100000/`.

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

The validated cold-run records and calls are saved as `cost/pilot_records.jsonl` and `cost/pilot_calls.jsonl`.
The warm replay evidence is saved in `cost/warm_resume_evidence.json`.
