"""Tests for domain value objects."""

from dataclasses import FrozenInstanceError

import pytest

from notificator.domain.value_objects import NotificationContent


def test_notification_content_defaults() -> None:
    """NotificationContent should expose defaults for optional fields."""
    content = NotificationContent(body="Hello")

    assert content.body == "Hello"
    assert content.subject is None
    assert content.html_body is None
    assert content.urgency is None


def test_notification_content_is_frozen() -> None:
    """NotificationContent should be immutable once created."""
    content = NotificationContent(body="Hello", subject="Subject")

    with pytest.raises(FrozenInstanceError):
        content.subject = "New"  # type: ignore[misc]
