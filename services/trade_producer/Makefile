# Variables
IMAGE_NAME := trade_producer
DEV_ENV_FILE := live.dev.env
PROD_ENV_FILE := live.prod.env
HISTORICAL_PROD_ENV_FILE := .env.historical.prod
LIVE_CONTAINER_NAME := trade-producer
HISTORICAL_CONTAINER_NAME := trade-producer-historical

# Phony targets
.PHONY: run-live-dev run-live-prod run-historical-prod build rebuild logs logs-historical lint format clean

# Development run
run-live-dev:
	cp $(DEV_ENV_FILE) .env
	poetry run python -m app.main

# Build Docker image
build:
	docker build -t $(IMAGE_NAME) .

# Rebuild Docker image without cache
rebuild:
	docker build --no-cache -t $(IMAGE_NAME) .

# Run live Docker container
run-live-prod:
	docker run \
		--network redpanda_network \
		--env-file $(PROD_ENV_FILE) \
		--restart unless-stopped \
		--volume "./app:/code/app" \
		--name $(LIVE_CONTAINER_NAME) \
		$(IMAGE_NAME) python -m app.main

run-historical-prod:
	docker run \
		--network redpanda_network \
		--env-file $(HISTORICAL_PROD_ENV_FILE) \
		--restart unless-stopped \
		--volume "./app:/code/app" \
		--name $(HISTORICAL_CONTAINER_NAME) \
		$(IMAGE_NAME) python -m app.main


logs: 
	docker logs -f $(LIVE_CONTAINER_NAME)
	
logs-historical:
	docker logs -f $(HISTORICAL_CONTAINER_NAME)

stop:
	docker stop $(LIVE_CONTAINER_NAME) || true
	docker stop $(HISTORICAL_CONTAINER_NAME) || true

# Lint code
lint:
	ruff check --fix .

# Format code
format:
	ruff format .

# Clean up
clean:
	@echo "Cleaning up..."
	@if docker ps -a --format '{{.Names}}' | grep -q "^$(LIVE_CONTAINER_NAME)$$"; then \
		echo "Stopping and removing $(LIVE_CONTAINER_NAME) container..."; \
		docker stop $(LIVE_CONTAINER_NAME); \
		docker rm $(LIVE_CONTAINER_NAME); \
	else \
		echo "$(LIVE_CONTAINER_NAME) container not found. Skipping."; \
	fi
	@if docker ps -a --format '{{.Names}}' | grep -q "^$(HISTORICAL_CONTAINER_NAME)$$"; then \
		echo "Stopping and removing $(HISTORICAL_CONTAINER_NAME) container..."; \
		docker stop $(HISTORICAL_CONTAINER_NAME); \
		docker rm $(HISTORICAL_CONTAINER_NAME); \
	else \
		echo "$(HISTORICAL_CONTAINER_NAME) container not found. Skipping."; \
	fi
	@if [ -f .env ]; then \
		echo "Removing .env file..."; \
		rm -f .env; \
	else \
		echo ".env file not found. Skipping."; \
	fi
	@echo "Clean up complete."