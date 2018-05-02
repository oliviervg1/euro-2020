.PHONY: clean
clean:
	- rm -rf env
	- find . -name "*.pyc" | xargs rm

env: requirements.txt requirements-dev.txt
	 virtualenv -p python3 env
	. env/bin/activate && pip install -r requirements.txt -r requirements-dev.txt

.PHONY: lint
lint: env
	. env/bin/activate && flake8 *.py

.PHONY: run
run: lint
	. env/bin/activate && python src/main.py
