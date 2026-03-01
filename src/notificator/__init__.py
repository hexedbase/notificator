"""Simplified notification delivery primitives and provider adapters."""

from notificator.domain import (
    AsyncClosable,
    EmailAddress,
    NotificationClient,
    NotificationContent,
    NotificationError,
    PhoneNumber,
)

__all__ = [
    "AsyncClosable",
    "EmailAddress",
    "NotificationClient",
    "NotificationContent",
    "NotificationError",
    "PhoneNumber",
]
