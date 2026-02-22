"""Domain primitives and ports for the notificator package."""

from notificator.domain.exceptions import NotificationError
from notificator.domain.ports import AsyncClosable, NotificationClient
from notificator.domain.value_objects import NotificationContent

__all__ = ["AsyncClosable", "NotificationClient", "NotificationContent", "NotificationError"]
