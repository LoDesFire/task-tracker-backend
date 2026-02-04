import logging
import uvloop

from app.services.kafka_consumer_service import KafkaConsumerService

logger = logging.getLogger(__name__)


async def main():
    kafka_consumer_service = KafkaConsumerService()
    await kafka_consumer_service.consume()


if __name__ == '__main__':
    try:
        uvloop.run(main())
    except KeyboardInterrupt:
        logger.info('Received interrupt signal')
