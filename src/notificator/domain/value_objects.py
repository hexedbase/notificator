from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class NotificationContent:
    """A unified domain object representing the notification payload."""

    body: str
    subject: str | None = None
    html_body: str | None = None
    urgency: str | None = None
