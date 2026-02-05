import logging
from datetime import datetime

import boto3
from botocore.exceptions import ClientError
from django.conf import settings

from helpers.exceptions import SESEmailsSendingExceptions

logger = logging.getLogger(__name__)


class SESService:
    def __init__(self, sender):
        self._session = boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_SES_REGION_NAME,
        )
        self._client = self._session.client(
            service_name="ses",
            endpoint_url=settings.AWS_SES_ENDPOINT_URL,
        )
        self._sender = sender

    def __send_batch_emails(self, *emails, subject: str, body: str):
        message_ids = []
        for slice_idx in range(
            0, len(emails), settings.AWS_SES_MAX_RECIPIENTS_PER_MESSAGE
        ):
            sliced_emails = emails[
                slice_idx : slice_idx + settings.AWS_SES_MAX_RECIPIENTS_PER_MESSAGE
            ]
            try:
                response = self._client.send_email(
                    Source=self._sender,
                    Destination={
                        "ToAddresses": [email for email in sliced_emails],
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
                logger.info(
                    "Email sent to %s, MessageId: %s",
                    str(emails),
                    str(response["MessageId"]),
                )
                message_ids.append(response["MessageId"])
            except ClientError as e:
                logger.error(
                    "Failed to send email to %s: %s",
                    str(emails),
                    str(e.response["Error"]["Message"]),
                )
                raise SESEmailsSendingExceptions(
                    sent_emails_count=slice_idx,
                    message_ids=message_ids,
                )

    def send_invitation_batch_emails(self, *emails, invitation_id: str):
        subject = "You have been invited in project"
        body = "Dear User,\n\nYour invitation is: {}".format(invitation_id)
        return self.__send_batch_emails(*emails, subject=subject, body=body)

    def send_deadline_batch_emails(
        self, *emails, deadline: datetime, task_title: str, project_title: str
    ):
        subject = "The deadline for the task {} is coming".format(task_title)
        body = "Deadline is {}. Project: {}".format(deadline.isoformat(), project_title)
        return self.__send_batch_emails(*emails, subject=subject, body=body)

    def send_status_changing_batch_emails(
        self, *emails, new_status, task_title: str, project_title: str
    ):
        subject = "Status subscription: Status in {} was updated!".format(task_title)
        body = "New status for the task is {}. Project: {}".format(
            new_status, project_title
        )
        return self.__send_batch_emails(*emails, subject=subject, body=body)
