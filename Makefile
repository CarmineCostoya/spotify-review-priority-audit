PYTHON ?= python3
FULL_CSV ?= course_material/spotify_reviews_18months.csv

.PHONY: test profile select demo cost-offline serve

test:
	PYTHONPATH=src $(PYTHON) -m unittest discover -s tests -v

profile:
	PYTHONPATH=src $(PYTHON) -m spotify_audit.cli profile --input "$(FULL_CSV)" --out outputs/ingestion_report.json

select:
	PYTHONPATH=src $(PYTHON) -m spotify_audit.cli select --input "$(FULL_CSV)" --out data/analysis_100000.csv --count 100000

demo:
	PYTHONPATH=src $(PYTHON) -m spotify_audit.cli run --input course_material/cost_100.csv --run-dir outputs/runs/dev-100 --provider heuristic --verify-count 10

cost-offline:
	PYTHONPATH=src $(PYTHON) -m spotify_audit.cli cost --calls cost/pilot_calls.jsonl --rates cost/rates.csv --out cost/report.md --projected-records 100000

serve:
	PYTHONPATH=src $(PYTHON) -m spotify_audit.cli serve --database outputs/spotify_audit.db --port 8000

