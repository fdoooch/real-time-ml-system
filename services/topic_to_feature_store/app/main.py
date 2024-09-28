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
import logging

logger = logging.getLogger(settings.LOGGER_NAME)


def topic_to_feature_store(
    kafka_broker_address: str,
    kafka_input_topic: str,
    kafka_consumer_group: str,
    feature_group_options: FeatureGroupOptions,
    start_offline_materialization: bool,
    batch_size: int,
) -> None:
    """
    Push feature from kafka to Hopsworks
    :param kafka_broker_address: Kafka broker address
    :param kafka_input_topic: Kafka topic to consume
    :param kafka_consumer_group_id: Kafka consumer group ID
    """
    logger.info("Starting application")
    app = Application(
        broker_address=kafka_broker_address,
        consumer_group=kafka_consumer_group,
        auto_offset_reset="earliest",
    )
    feature_group = get_or_create_feature_group(
        options=feature_group_options,
    )

    batch = []
    with app.get_consumer() as consumer:
        consumer.subscribe(topics=[kafka_input_topic])

        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                logger.error(f"Kafka error: {msg.error()}")
                continue
            
            features = json.loads(msg.value().decode("utf-8"))
            batch.append(features)

            if len(batch) < batch_size:
                logger.debug(f'Batch has size {len(batch)} < {batch_size:,}...')
                continue

            logger.debug(f'Batch has size {len(batch)} >= {batch_size:,}... Pushing data to Feature Store')
            push_feature_to_feature_group(
                value=batch,
                feature_group=feature_group,
                start_offline_materialization=start_offline_materialization,
            )

            batch = []
            # push_feature_to_feature_store(
            #     options=feature_group_options,
            #     creds=feature_group_creds,
            #     feature=feature,
            #     start_offline_materialization=start_offline_materialization,
            # )
            # Storing offset only after the message is processed enables at-least-once processing
            consumer.store_offsets(message=msg)



def main():
    feature_group_creds = FeatureGroupCreds(
        project_name=settings.hopsworks.PROJECT_NAME,
        api_key=settings.hopsworks.API_KEY,
    )
    feature_group_options = FeatureGroupOptions(
        name=settings.hopsworks.FEATURE_GROUP_NAME,
        version=settings.hopsworks.FEATURE_GROUP_VERSION,
        primary_key=settings.hopsworks.FEATURE_GROUP_PRIMARY_KEY,
        event_time=settings.hopsworks.FEATURE_GROUP_EVENT_TIME,
        online_enabled=True,
        creds=feature_group_creds,
    )
    topic_to_feature_store(
        kafka_broker_address=settings.kafka.BROKER_ADDRESS,
        kafka_input_topic=settings.kafka.INPUT_TOPIC,
        kafka_consumer_group=settings.kafka.CONSUMER_GROUP,
        feature_group_options=feature_group_options,
        start_offline_materialization=settings.hopsworks.START_OFFLINE_MATERIALIZATION,
        batch_size=settings.hopsworks.PUSHING_BATCH_SIZE
    )


if __name__ == "__main__":
    main()