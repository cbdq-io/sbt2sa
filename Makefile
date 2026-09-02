.EXPORT_ALL_VARIABLES:

COMPOSE_FILE = tests/resources/docker-compose.yaml
TAG = 1.0.5

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
	pip install -U -r requirements.txt -r requirements-dev.txt
	pip check
