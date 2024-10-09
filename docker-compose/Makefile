start-redpanda:
	docker compose -f redpanda.yml up -d

stop-redpanda:
	docker compose -f redpanda.yml down

start-feature-pipeline:
	docker compose -f feature_live_pipeline.yml up --build -d

stop-feature-pipeline:
	docker compose -f feature_live_pipeline.yml down

start-backfill-pipeline:
	export BACKFILL_JOB_ID=$$(date +%s%N)-$$RANDOM && \
	echo $$BACKFILL_JOB_ID > .backfill_job_id && \
	docker compose -f backfill_pipeline.yml up --build -d -e BACKFILL_JOB_ID=$$BACKFILL_JOB_ID && \
	echo "Started backfill pipeline with job id: $$BACKFILL_JOB_ID"

stop-backfill-pipeline:
	$(eval BACKFILL_JOB_ID := $(shell cat .backfill_job_id))
	@echo "Stopping backfill pipeline with job id: $(BACKFILL_JOB_ID)"
	docker compose -f backfill_pipeline.yml down
	@echo "Deleting Redpanda resources for job id: $(BACKFILL_JOB_ID)"
	@make delete-redpanda-resources BACKFILL_JOB_ID=$(BACKFILL_JOB_ID)
	@rm -f .backfill_job_id
	
delete-redpanda-resources:
	rpk topic delete trade_historical_$(BACKFILL_JOB_ID) -- brokers redpanda-0:9092
	rpk topic delete ohlcv_historical_$(BACKFILL_JOB_ID) -- brokers redpanda-0:9092
	rpk group delete trade_to_ohlcv_historical_$(BACKFILL_JOB_ID) -- brokers redpanda-0:9092
	rpk group delete ohlcv_historical_to_feature_store_$(BACKFILL_JOB_ID) -- brokers redpanda-0:9092


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