.PHONY: install run-local clean-up test format lint

install:
	poetry install --with dev

run-local:
	docker-compose -f docker/docker-compose.yml up --build

clean-up:
	docker-compose -f docker/docker-compose.yml down -v

test:
	poetry run pytest tests/ --cov=app --cov-report=term-missing

format:
	poetry run isort app tests
	poetry run black app tests

lint:
	poetry run isort --check-only app tests
	poetry run black --check app tests
	poetry run flake8 app tests

