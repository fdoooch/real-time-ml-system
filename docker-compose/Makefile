start-redpanda:
	docker compose -f redpanda.yml up -d

stop-redpanda:
	docker compose -f redpanda.yml down

start-feature-live-pipeline:
	docker compose -f feature_live_pipeline.yml up -d

stop-feature-live-pipeline:
	docker compose -f feature_live_pipeline.yml down


logs-trades-producer-live:
	docker logs trades-producer -f

logs-trades-to-ohlcv-live:
	docker logs trades-to-ohlcv -f

logs-feature-live-pipeline:
	docker logs feature-live-pipeline -f