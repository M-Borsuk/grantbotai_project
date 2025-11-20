.PHONY: install run test format lint

install:
	poetry install --with dev

run:
	poetry run uvicorn app.main:app --reload

test:
	poetry run pytest tests

format:
	poetry run isort app tests
	poetry run black app tests

lint:
	poetry run isort --check-only app tests
	poetry run black --check app tests
	poetry run flake8 app tests

