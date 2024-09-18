build:
	docker build --no-cache -t trade_producer .

run:
	docker run --network redpanda_network trade_producer

lint:
	ruff check --fix


format:
	ruff format .