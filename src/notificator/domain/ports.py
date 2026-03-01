"""Domain-facing interfaces for notification delivery clients."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from notificator.domain.value_objects import NotificationContent


@runtime_checkable
class AsyncClosable(Protocol):
    """Port for safely tearing down infrastructure adapters."""

    async def aclose(self) -> None:
        """Release any held resources and close open connections."""


class NotificationClient[RecipientT: str](Protocol):
    """Protocol for notification transports (email, SMS, etc.)."""

    async def notify(self, content: NotificationContent, *, recipient: RecipientT) -> None:
        """Send a notification payload to a recipient.

        Args:
            content: Notification payload describing body, subject, and other metadata.
            recipient: Transport-specific recipient identifier (email, phone, etc.).
        """

    async def notify_from_template(
        self, template: str, *, recipient: RecipientT, version: str | None = None, **variables: str
    ) -> None:
        """Send a notification using a stored template and variables.

        Args:
            template: Provider template identifier.
            recipient: Transport-specific recipient identifier (email, phone, etc.).
            version: Optional provider template version alias or ID.
            **variables: Template variables to inject into the message.
        """
