from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from notificator.domain.value_objects import NotificationContent


@runtime_checkable
class AsyncClosable(Protocol):
    """Port for safely tearing down infrastructure adapters."""

    async def aclose(self) -> None: ...


class NotificationClient[RecipientT: str](Protocol):
    async def notify(self, content: NotificationContent, *, recipient: RecipientT) -> None: ...

    async def notify_from_template(
        self, template: str, *, recipient: RecipientT, version: str | None = None, **variables: str
    ) -> None: ...
