#!.venv/bin/python
import json

from settings.general_settings import settings


def print_settings():
    settings_json = json.dumps(settings.model_dump(), indent=4, default=str)
    print(settings_json)


if __name__ == "__main__":
    print_settings()
