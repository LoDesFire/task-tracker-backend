import asyncio
import json
import threading
from functools import partial
from typing import Callable

import aioboto3
from types_aiobotocore_s3.client import S3Client

from src.settings.general_settings import settings


class S3Dependency:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(S3Dependency, cls).__new__(cls)
                    cls._instance._initialize_session()
        return cls._instance

    def _initialize_session(self):
        self._session = aioboto3.Session()
        self._s3_client = partial(
            self._session.client,
            "s3",
            region_name=settings.aws_settings.region_name,
            endpoint_url=settings.aws_settings.endpoint_url,
            aws_access_key_id=settings.aws_settings.access_key_id.get_secret_value(),
            aws_secret_access_key=settings.aws_settings.secret_access_key.get_secret_value(),  # noqa: E501
        )

    @property
    def s3_client_factory(self) -> Callable[[], S3Client]:
        return self._s3_client

async def main():
    s3_client_factory = S3Dependency().s3_client_factory

    async with s3_client_factory() as s3_client:
        # print(json.dumps(await s3_client.list_objects_v2(
        #     Bucket="todo-file-microservice",
        # ), indent=2, default=str))

        policy = dict(
            Version="2012-10-17",
            Statement=[
                dict(
                    Effect="Deny",
                    Action=["s3:*"],
                    Resource=["arn:aws:s3:::*"],
                    Principal="*",
                )
            ],
        )
        await s3_client.put_bucket_policy(
            Bucket=settings.aws_settings.s3_service_bucket_name,
            Policy=json.dumps(policy),
        )


if __name__ == '__main__':
    asyncio.run(main())