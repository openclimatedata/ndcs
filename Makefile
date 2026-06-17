all:
	git pull
	uv run playwright install firefox
	uv run scripts/process.py
	@git diff data

download: data/ndcs.csv venv
	./venv/bin/python scripts/download.py

clean:
	rm -rf data/*.csv
	rm -rf pdfs/*.pdf

.PHONY: clean download
