from app.config import settings
from app.hopsworks_api import push_feature_to_store, FeatureGroupOptions, FeatureGroupCreds

from quixstreams import Application
import json
import logging

logger = logging.getLogger(settings.LOGGER_NAME)


def topic_to_feature_store(
    kafka_broker_address: str,
    kafka_input_topic: str,
    kafka_consumer_group: str,
    feature_group_options: FeatureGroupOptions,
    feature_group_creds: FeatureGroupCreds,
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
    with app.get_consumer() as consumer:
        consumer.subscribe(topics=[kafka_input_topic])

        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                logger.error(f"Kafka error: {msg.error()}")
                continue
            
            feature = json.loads(msg.value().decode("utf-8"))
            push_feature_to_store(
                feature=feature,
                options=feature_group_options,
                creds=feature_group_creds,
            )
            breakpoint()
            # Storing offset only after the message is processed enables at-least-once processing
            consumer.store_offsets(message=msg)



def main():
    feature_group_options = FeatureGroupOptions(
        name=settings.hopsworks.FEATURE_GROUP_NAME,
        version=settings.hopsworks.FEATURE_GROUP_VERSION,
        primary_key=["timestamp"],
        event_time="timestamp",
        online_enabled=True,
    )
    feature_group_creds = FeatureGroupCreds(
        project_name=settings.hopsworks.PROJECT_NAME,
        api_key=settings.hopsworks.API_KEY,
    )
    topic_to_feature_store(
        kafka_broker_address=settings.kafka.BROKER_ADDRESS,
        kafka_input_topic=settings.kafka.INPUT_TOPIC,
        kafka_consumer_group=settings.kafka.CONSUMER_GROUP,
        feature_group_options=feature_group_options,
        feature_group_creds=feature_group_creds,
    )


if __name__ == "__main__":
    main()