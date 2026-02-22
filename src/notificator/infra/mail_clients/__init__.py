"""Email provider integrations and related errors."""

from notificator.infra.mail_clients.exceptions import (
    EmailNotificationMissingSubjectError,
    MailAPIError,
    MalformedRecipientEmailError,
    MissingClientAuthError,
)
from notificator.infra.mail_clients.mailgun_client import MailgunClient

__all__ = [
    "EmailNotificationMissingSubjectError",
    "MailAPIError",
    "MailgunClient",
    "MalformedRecipientEmailError",
    "MissingClientAuthError",
]
