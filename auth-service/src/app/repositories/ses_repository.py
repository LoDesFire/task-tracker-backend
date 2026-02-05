from typing import Callable

from types_aiobotocore_ses.client import SESClient

from src.settings.general_settings import settings


class SESRepository:
    def __init__(self, ses_client_factory: Callable[[], SESClient]):
        self.__ses_client_factory = ses_client_factory

    async def __send_email(self, email: str, subject: str, body: str):
        async with self.__ses_client_factory() as client:
            client: SESClient  # type: ignore
            await client.send_email(
                Source=settings.ses_source_email,
                Destination={
                    "ToAddresses": [email],
                },
                Message={
                    "Subject": {
                        "Data": subject,
                    },
                    "Body": {
                        "Text": {
                            "Data": body,
                        }
                    },
                },
            )

    async def send_password_reset_email(self, email: str, password: str):
        subject = "Password Reset Request"
        body = "Your password has been reset.\nThe new password is: {}".format(password)

        await self.__send_email(email, subject, body)

    async def send_verification_code_email(self, email: str, verification_code: str):
        subject = "Verification Code Request"
        body = "Your verification code is {}.".format(verification_code)

        await self.__send_email(email, subject, body)
