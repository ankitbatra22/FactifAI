.PHONY: install update-deps clean format lint test

install:
	pip install -r backend/requirements/requirements.txt

update-deps:
	cd backend && pip-compile requirements/requirements.in --upgrade
	pip install -r backend/requirements/requirements.txt

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

format:
	black backend
	isort backend

lint:
	flake8 backend
	mypy backend

test:
	pytest backend/tests/ -v