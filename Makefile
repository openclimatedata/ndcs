all: data/ndcs.csv venv

venv: scripts/requirements.txt
	[ -d ./venv ] || python3 -m venv venv
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -Ur scripts/requirements.txt
	touch venv

download: data/ndcs.csv venv
	./venv/bin/python scripts/download.py

data/ndcs.csv: scripts/process.py venv
	./venv/bin/python scripts/process.py

clean:
	rm -rf data/*.csv
	rm -rf pdfs/*.pdf

.PHONY: clean download
