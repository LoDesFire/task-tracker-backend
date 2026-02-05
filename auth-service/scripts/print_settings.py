#!.venv/bin/python
import json
import logging

from src.settings.general_settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def print_settings():
    settings_json = json.dumps(settings.model_dump(), indent=4, default=str)
    logger.info(settings_json)


if __name__ == "__main__":
    print_settings()
