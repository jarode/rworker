# Makefile dla SPA Automation
# Wzorowany na oficjalnym b24pysdk: https://github.com/bitrix24/b24pysdk

.PHONY: help build-dev build test test-unit test-integration lint format clean run-webhook shell

help: ## Pokaż dostępne komendy
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

build-dev: ## Zbuduj dev image (tylko raz)
	docker compose build spa-dev

build: ## Zbuduj wszystkie images
	docker compose build

test: ## Uruchom wszystkie testy
	docker compose run --rm spa-test

test-unit: ## Uruchom tylko testy jednostkowe
	docker compose run --rm spa-test pytest tests/unit/ -v

test-integration: ## Uruchom tylko testy integracyjne
	docker compose run --rm spa-test pytest tests/integration/ -v

test-watch: ## Uruchom testy w trybie watch
	docker compose run --rm spa-test pytest-watch tests/

lint: ## Uruchom lintery
	docker compose run --rm spa-dev flake8 src/ tests/
	docker compose run --rm spa-dev mypy src/

format: ## Formatuj kod
	docker compose run --rm spa-dev black src/ tests/
	docker compose run --rm spa-dev isort src/ tests/

run-webhook: ## Uruchom webhook service
	docker compose up spa-webhook

run-dev: ## Uruchom dev container (interactive)
	docker compose run --rm --service-ports spa-dev bash

shell: ## Otwórz shell w dev container
	docker compose run --rm spa-dev bash

clean: ## Wyczyść cache i temp files
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	docker compose down -v

rebuild: clean build ## Wyczyść i przebuduj

logs: ## Pokaż logi webhook
	docker compose logs -f spa-webhook

ps: ## Pokaż running containers
	docker compose ps

# Quick commands
up: ## Start webhook service
	docker compose up -d spa-webhook

down: ## Stop wszystkie services
	docker compose down

restart: down up ## Restart webhook service

