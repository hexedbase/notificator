"""Tests for domain ports and protocols."""

import asyncio

from notificator.domain.ports import AsyncClosable


class DummyClosable:
    """Simple implementation of AsyncClosable for runtime checks."""

    def __init__(self) -> None:
        """Initialize the dummy closable object."""
        self.closed = False

    async def aclose(self) -> None:
        """Close the dummy client."""
        self.closed = True


def test_async_closable_runtime_check() -> None:
    """AsyncClosable should support runtime structural checks."""
    dummy = DummyClosable()

    assert isinstance(dummy, AsyncClosable)

    asyncio.run(dummy.aclose())
    assert dummy.closed is True
