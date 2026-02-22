"""Base module for mail clients exceptions."""

from notificator.domain.exceptions import NotificationError


class MailNotificationError(NotificationError):
    """Base exception for mail clients errors."""


class MalformedClientUrlError(MailNotificationError):
    """Exception raised when mail client base_url is malformed."""

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url
        super().__init__(f"{self.base_url} is not a valid url.")


class MalformedRecipientEmailError(MailNotificationError):
    """Exception raised when a recipient email is malformed."""

    def __init__(self, recipient: str) -> None:
        self.recipient = recipient
        super().__init__(f"{self.recipient} is not a valid email address")


class MissingClientAuthError(MailNotificationError):
    """Exception raised when a mailclient authorization is missing."""

    def __init__(self) -> None:
        super().__init__("You need to either provide an `api_key` or a configured httpx client.")


class MailAPIError(MailNotificationError):
    """Exception raised when an error occurs while making an API call."""


class EmailNotificationMissingSubjectError(MailNotificationError):
    """Exception raised when an email notification is missing a subject."""

    def __init__(self) -> None:
        super().__init__(
            "You need to either provide a subject for email NotificationContent "
            "or set a default_subject for compatible clients."
        )
