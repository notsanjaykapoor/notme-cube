# venv created with 'uv venv --python /Users/sanjaykapoor/.pyenv/shims/python3.12'
VENV = .venv
PIP = pip
PYTHON = $(VENV)/bin/python3
SHELL = /bin/bash

.PHONY: build clean dev deploy docker install prd test

build:
	./scripts/docker-utils build

deploy:
	./scripts/vps/vps-utils deploy --host 5.161.208.47 --user root

dev:
	make -j 2 dev-server dev-bot

dev-bot:
	. $(VENV)/bin/activate && ./bin/deploy-bot run

dev-server:
	. $(VENV)/bin/activate && ./bin/app-server --port 9003

install: pyproject.toml
	uv sync

prd:
	. $(VENV)/bin/activate && ./bin/app-server --port 9003

test:
	. $(VENV)/bin/activate && pytest

clean:
	rm -rf __pycache__
	rm -rf $(VENV)
