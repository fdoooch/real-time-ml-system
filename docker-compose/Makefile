start-redpanda:
	docker compose -f redpanda.yml up -d

stop-redpanda:
	docker compose -f redpanda.yml down

start-feature-pipeline:
	docker compose -f feature_live_pipeline.yml up --build -d

stop-feature-pipeline:
	docker compose -f feature_live_pipeline.yml down

start-backfill-pipeline:
	export BACKFILL_JOB_ID=$$(date +%s) && \
	echo $$BACKFILL_JOB_ID > .backfill_job_id && \
	BACKFILL_JOB_ID=$$BACKFILL_JOB_ID docker compose -f backfill_pipeline.yml up --build -d && \
	echo "Started backfill pipeline with job id: $$BACKFILL_JOB_ID"

stop-backfill-pipeline:
	$(eval BACKFILL_JOB_ID := $(shell cat .backfill_job_id))
	@echo "Stopping backfill pipeline with job id: $(BACKFILL_JOB_ID)"
	docker compose -f backfill_pipeline.yml down
	@echo "Attempting to delete Redpanda resources for job id: $(BACKFILL_JOB_ID)"
	@make delete-redpanda-resources BACKFILL_JOB_ID=$(BACKFILL_JOB_ID) || \
		(echo "Warning: Failed to delete Redpanda resources. Please ensure 'rpk' is installed and accessible." && \
		echo "You may need to manually delete the following resources:" && \
		echo "- Topic: trade_historical_$(BACKFILL_JOB_ID)" && \
		echo "- Topic: ohlcv_historical_$(BACKFILL_JOB_ID)" && \
		echo "- Consumer group: trade_to_ohlcv_historical_$(BACKFILL_JOB_ID)" && \
		echo "- Consumer group: ohlcv_historical_to_feature_store_$(BACKFILL_JOB_ID)")
	@rm -f .backfill_job_id

delete-redpanda-resources:
	@which rpk > /dev/null || (echo "Error: 'rpk' command not found. Please install it or add it to your PATH." && exit 1)
	rpk topic delete trade_historical_$(BACKFILL_JOB_ID) -- brokers redpanda-0:9092 || true
	rpk topic delete ohlcv_historical_$(BACKFILL_JOB_ID) -- brokers redpanda-0:9092 || true
	rpk group delete trade_to_ohlcv_historical_$(BACKFILL_JOB_ID) -- brokers redpanda-0:9092 || true
	rpk group delete ohlcv_historical_to_feature_store_$(BACKFILL_JOB_ID) -- brokers redpanda-0:9092 || true


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