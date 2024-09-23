from .config import settings

from quixstreams import Application
import logging

logger = logging.getLogger(settings.LOGGER_NAME)


def topic_to_feature_store(
    kafka_broker_address: str,
    kafka_input_topic: str,
    kafka_consumer_group: str,
    feature_group_name: str,
    feature_group_version: int,
) -> None:
    """
    Push feature from kafka to Hopsworks
    :param kafka_broker_address: Kafka broker address
    :param kafka_input_topic: Kafka topic to consume
    :param kafka_consumer_group_id: Kafka consumer group ID
    :param feature_group_name: Hopsworks feature group name
    :param feature_group_version: Hopsworks feature group version
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
            
            feature = msg.value().decode("utf-8")
            breakpoint()


def push_feature_to_to_store(
        feature: dict,
        feature_group_name: str,
        feature_group_version: int
) -> None:
    ...



def main():
    topic_to_feature_store(
        kafka_broker_address=settings.kafka.BROKER_ADDRESS,
        kafka_input_topic=settings.kafka.INPUT_TOPIC,
        kafka_consumer_group=settings.kafka.CONSUMER_GROUP,
        feature_group_name=settings.hopsworks.FEATURE_GROUP_NAME,
        feature_group_version=settings.hopsworks.FEATURE_GROUP_VERSION
    )


if __name__ == "__main__":
    main()