from app.config import settings
from app.hopsworks_api import (
    push_feature_to_feature_group,
    # push_feature_to_feature_store,
    get_or_create_feature_group, 
    FeatureGroupOptions, 
    FeatureGroupCreds,
)

from quixstreams import Application
import json
import time
import logging
from dataclasses import dataclass

logger = logging.getLogger(settings.LOGGER_NAME)


@dataclass
class KafkaOptions:
    broker_address: str
    input_topic: str
    consumer_group: str
    auto_offset_reset: str = "latest"


def topic_to_feature_store(
    kafka_options: KafkaOptions,
    feature_group_options: FeatureGroupOptions,
    start_offline_materialization: bool,
    batch_size: int,
    pause_between_pushing: int = 0,
) -> None:
    """
    Push feature from kafka to Hopsworks
    :param kafka_broker_address: Kafka broker address
    :param kafka_input_topic: Kafka topic to consume
    :param kafka_consumer_group_id: Kafka consumer group ID
    """
    logger.info("Starting application")
    app = Application(
        broker_address=kafka_options.broker_address,
        consumer_group=kafka_options.consumer_group,
        auto_offset_reset=kafka_options.auto_offset_reset,
    )
    feature_group = get_or_create_feature_group(
        options=feature_group_options,
    )

    batch = []
    with app.get_consumer() as consumer:
        consumer.subscribe(topics=[kafka_options.input_topic])

        while True:
            msg = consumer.poll(timeout=300.0)
            if msg is None:
                if len(batch) > 0:
                    logger.debug(f'Batch has size {len(batch)} > 0... Pushing data to Feature Store by Timeout')
                    push_feature_to_feature_group(
                        value=batch,
                        feature_group=feature_group,
                        start_offline_materialization=start_offline_materialization,
                    )
                    batch = []
                    time.sleep(pause_between_pushing)
                    continue
                else:
                    logger.info("No data received from Kafka. Exiting...")
                    break
            if msg.error():
                logger.error(f"Kafka error: {msg.error()}")
                continue
            
            features = json.loads(msg.value().decode("utf-8"))
            batch.append(features)

            if len(batch) < batch_size:
                print(f'Batch has size {len(batch)} < {batch_size:,}...', end='\r')
                continue

            logger.debug(f'Batch has size {len(batch)} >= {batch_size:,}... Pushing data to Feature Store')
            push_feature_to_feature_group(
                value=batch,
                feature_group=feature_group,
                start_offline_materialization=start_offline_materialization,
            )

            batch = []
            time.sleep(pause_between_pushing)
            consumer.store_offsets(message=msg)



def main():
    kafka_options = KafkaOptions(
        broker_address=settings.kafka.BROKER_ADDRESS,
        input_topic=settings.kafka.INPUT_TOPIC,
        consumer_group=settings.kafka.CONSUMER_GROUP,
        auto_offset_reset=settings.kafka.AUTO_OFFSET_RESET,
    )
    feature_group_creds = FeatureGroupCreds(
        project_name=settings.hopsworks.PROJECT_NAME,
        api_key=settings.hopsworks.API_KEY,
    )
    feature_group_options = FeatureGroupOptions(
        name=settings.hopsworks.FEATURE_GROUP_NAME,
        version=settings.hopsworks.FEATURE_GROUP_VERSION,
        primary_key=settings.hopsworks.FEATURE_GROUP_PRIMARY_KEY,
        event_time=settings.hopsworks.FEATURE_GROUP_EVENT_TIME,
        online_enabled=settings.hopsworks.FEATURE_GROUP_ONLINE_ENABLED,
        creds=feature_group_creds,
    )
    topic_to_feature_store(
        kafka_options=kafka_options,
        feature_group_options=feature_group_options,
        start_offline_materialization=settings.hopsworks.START_OFFLINE_MATERIALIZATION,
        batch_size=settings.hopsworks.PUSHING_BATCH_SIZE,
        pause_between_pushing=settings.hopsworks.PAUSE_BETWEEN_PUSHING,
    )


if __name__ == "__main__":
    import hsfs

    logger.info("Starting application")
    logger.debug(f"HSFS version: {hsfs.__version__}")

    main()