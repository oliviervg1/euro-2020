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

.PHONY: deploy-work-staging
deploy-work-staging: lint
	cp src/config/config-work.cfg src/config/config.cfg
	. env/bin/activate && zappa update staging_work
	. env/bin/activate && zappa update staging_work_scoring

.PHONY: deploy-work-production
deploy-work-production: lint
	cp src/config/config-work.cfg src/config/config.cfg
	. env/bin/activate && zappa update production_work
	. env/bin/activate && zappa update production_work_scoring

.PHONY: deploy-personal
deploy-personal: lint
	cp src/config/config-personal.cfg src/config/config.cfg
	. env/bin/activate && zappa update production_personal
	. env/bin/activate && zappa update production_personal_scoring
