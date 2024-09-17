# venv created with 'uv venv --python /Users/sanjaykapoor/.pyenv/shims/python3.12'
VENV = .venv
PIP = pip
PYTHON = $(VENV)/bin/python3
SHELL = /bin/bash

.PHONY: build clean dev deploy docker install prd test

build:
	./scripts/vps/vps-utils build

deploy:
	./scripts/vps/vps-utils deploy --host 5.161.208.47 --user root

dev: docker
	. $(VENV)/bin/activate && ./bin/app-server --port 9003

docker:
	docker compose -f docker/docker-compose.yml up -d --no-recreate nats

install: requirements.txt
	uv pip install -r requirements.txt

prd:
	. $(VENV)/bin/activate && ./bin/app-server --port 9003

test:
	. $(VENV)/bin/activate && pytest

clean:
	rm -rf __pycache__
	rm -rf $(VENV)
