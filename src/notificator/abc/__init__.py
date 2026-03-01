"""Abstract ports for notification delivery."""

from __future__ import annotations

import importlib
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from collections.abc import Callable

    from notificator.domain.ports import AsyncClosable, NotificationClient


def _load_async_closable() -> object:
    module = importlib.import_module("notificator.domain.ports")
    return module.AsyncClosable


def _load_notification_client() -> object:
    module = importlib.import_module("notificator.domain.ports")
    return module.NotificationClient


_EXPORTS: Final[dict[str, Callable[[], object]]] = {
    "AsyncClosable": _load_async_closable,
    "NotificationClient": _load_notification_client,
}

__all__ = ("AsyncClosable", "NotificationClient")


def __getattr__(name: str) -> object:
    """Lazily load notification ports."""
    try:
        loader = _EXPORTS[name]
    except KeyError as exc:
        msg = f"module {__name__!r} has no attribute {name!r}"
        raise AttributeError(msg) from exc
    value = loader()
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    """Return module attributes for introspection tools."""
    return sorted(__all__)
