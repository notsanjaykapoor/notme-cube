# venv created with 'uv venv --python /Users/sanjaykapoor/.pyenv/shims/python3.12'
VENV = .venv
PIP = pip
PYTHON = $(VENV)/bin/python3

.PHONY: clean dev docker install test

dev: docker
	. $(VENV)/bin/activate
	./bin/app-server --port 9003

docker:
	docker compose -f docker/docker-compose.yml up -d --no-recreate nats

install: requirements.txt
	uv pip install -r requirements.txt

test:
	. $(VENV)/bin/activate
	pytest

clean:
	rm -rf __pycache__
	rm -rf $(VENV)
