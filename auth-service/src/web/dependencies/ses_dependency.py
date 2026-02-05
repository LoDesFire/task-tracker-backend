import threading
from functools import partial
from typing import Callable

import aioboto3
from types_aiobotocore_ses.client import SESClient

from src.settings.general_settings import settings


class SESDependency:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(SESDependency, cls).__new__(cls)
                    cls._instance._initialize_session()
        return cls._instance

    def _initialize_session(self):
        self._session = aioboto3.Session()
        self._ses_client = partial(
            self._session.client,
            "ses",
            region_name=settings.aws_settings.region_name,
            endpoint_url=settings.aws_settings.endpoint_url,
            aws_access_key_id=settings.aws_settings.access_key_id.get_secret_value(),
            aws_secret_access_key=settings.aws_settings.secret_access_key.get_secret_value(),  # noqa: E501
        )

    @property
    def ses_client_factory(self) -> Callable[[], SESClient]:
        return self._ses_client
