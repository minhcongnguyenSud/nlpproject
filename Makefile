# AI Newsletter Generator - Docker Commands

.PHONY: help build up down logs clean restart shell

help: ## Show this help message
	@echo "AI Newsletter Generator - Docker Commands"
	@echo "========================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Build the Docker images
	docker-compose build

up: ## Start the services
	docker-compose up -d

down: ## Stop the services
	docker-compose down

logs: ## View logs
	docker-compose logs -f

clean: ## Clean up containers, images, and volumes
	docker-compose down -v --rmi all

restart: ## Restart the services
	docker-compose restart

shell: ## Open a shell in the running container
	docker-compose exec newsletter-generator /bin/bash

dev: ## Start development environment
	docker-compose -f docker-compose.dev.yml up

dev-build: ## Build and start development environment
	docker-compose -f docker-compose.dev.yml up --build

test: ## Run tests
	docker-compose exec newsletter-generator python tests/test_setup.py

generate: ## Generate a newsletter manually
	docker-compose exec newsletter-generator python main.py

status: ## Show container status
	docker-compose ps
