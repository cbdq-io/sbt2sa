.EXPORT_ALL_VARIABLES:

COMPOSE_FILE = tests/resources/docker-compose.yaml
TAG = 0.1.0

all: lint clean build test

build:
	docker compose build

clean:
	docker compose down -t 0 --remove-orphans

cleanall: clean
	docker system prune -a --volumes --force

lint:
	docker run --rm -i hadolint/hadolint < Dockerfile
	yamllint -s .
	isort -v .
	flake8

sutlogs:
	docker compose logs sut

tag:
	@echo $(TAG)

test:
	docker compose up -d emulators --wait
	python ./tests/resources/create_dl_message.py
	docker compose up -d sut --wait
	PYTHONPATH=. pytest

prereqs:
	docker run --entrypoint /bin/sh mcr.microsoft.com/azure-functions/python:4-python3.14-appservice -c "pip freeze" > constraints.txt
	pip install -Uc constraints.txt -r requirements.txt -r requirements-dev.txt
	pip check
