.PHONY: infra
infra:
	cd infra/ && ./infra.sh

.PHONY: clean
clean:
	- rm -rf env
	- find . -name "*.pyc" | xargs rm

env: requirements.txt requirements-dev.txt
	 virtualenv -p python3 env
	. env/bin/activate && pip install -r requirements.txt -r requirements-dev.txt

.PHONY: lint
lint: env
	. env/bin/activate && flake8 src/

.PHONY: build
build: lint
ifndef TAG
	$(error TAG environment variable hasn't been defined!)
endif
ifndef GCP_PROJECT
	$(error GCP_PROJECT environment variable hasn't been defined!)
endif
	docker build \
		-t gcr.io/${GCP_PROJECT}/euro-2020:${TAG} \
		-t gcr.io/${GCP_PROJECT}/euro-2020:latest \
		.

.PHONY: push
push: build
	gcloud config set project ${GCP_PROJECT}
	gcloud auth configure-docker
	docker push gcr.io/${GCP_PROJECT}/euro-2020:${TAG}
	docker push gcr.io/${GCP_PROJECT}/euro-2020:latest

.PHONY: run_locally
run_locally:
ifndef TAG
	$(error TAG environment variable hasn't been defined!)
endif
ifndef GCP_PROJECT
	$(error GCP_PROJECT environment variable hasn't been defined!)
endif
	docker run \
		-p 8000:8000 \
		-e PORT=8000 \
		gcr.io/${GCP_PROJECT}/euro-2020:${TAG} \

.PHONY: deploy
deploy:
	echo 'Not implemented yet!'
