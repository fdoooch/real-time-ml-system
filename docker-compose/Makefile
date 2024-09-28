start-redpanda:
	docker compose -f redpanda.yml up -d

stop-redpanda:
	docker compose -f redpanda.yml down

start-feature-pipeline:
	docker compose -f feature_live_pipeline.yml up --build -d

stop-feature-pipeline:
	docker compose -f feature_live_pipeline.yml down

start-backfill-pipeline:
	docker compose -f backfill_pipeline.yml up --build -d

stop-backfill-pipeline:
	docker compose -f backfill_pipeline.yml down

logs-trades-producer-live:
	docker logs trades-producer -f

logs-trades-to-ohlcv-live:
	docker logs trades-to-ohlcv -f

logs-topic-to-feature-store-live:
	docker logs topic-to-feature-store -f


logs-trades-producer-historical:
	docker logs trades-producer-historical -f

logs-trades-to-ohlcv-historical:
	docker logs trades-to-ohlcv-historical -f

logs-topic-to-feature-store-historical:
	docker logs topic-to-feature-store-historical -f