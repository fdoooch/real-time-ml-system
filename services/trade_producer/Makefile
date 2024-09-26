# Variables
IMAGE_NAME := trade_producer
DEV_ENV_FILE := live.dev.env
PROD_ENV_FILE := live.prod.env
LIVE_CONTAINER_NAME := trade-producer
HISTORICAL_CONTAINER_NAME := trade-producer-historical

# Phony targets
.PHONY: run-live-dev run-live-prod build rebuild run-live lint format clean

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
run-live: build
	docker run \
		--network redpanda_network \
		--env-file $(PROD_ENV_FILE) \
		--restart unless-stopped \
		--volume "./code:/code" \
		--name $(LIVE_CONTAINER_NAME) \
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
	docker stop $(LIVE_CONTAINER_NAME) || true
	docker stop $(HISTORICAL_CONTAINER_NAME) || true
	docker rm $(LIVE_CONTAINER_NAME) || true
	docker rm $(HISTORICAL_CONTAINER_NAME) || true
	rm -f .env