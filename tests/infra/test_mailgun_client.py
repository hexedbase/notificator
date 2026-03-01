"""Tests for the Mailgun email client."""

import asyncio
from typing import cast

import httpx
import pytest

from notificator.domain.value_objects import NotificationContent
from notificator.infra.mail_clients.exceptions import (
    EmailNotificationMissingSubjectError,
    MailAPIError,
    MalformedClientUrlError,
    MalformedRecipientEmailError,
    MissingClientAuthError,
)
from notificator.infra.mail_clients.mailgun_client import EmailAddress, MailgunClient


class FakeAsyncClient:
    """Fake httpx client for Mailgun tests."""

    def __init__(
        self,
        *,
        auth: tuple[str, str] | None = None,
        raise_error: Exception | None = None,
        status_code: int = 200,
    ) -> None:
        """Initialize the fake HTTP client."""
        self.auth = auth
        self.raise_error = raise_error
        self.status_code = status_code
        self.calls: list[tuple[str, dict[str, str], tuple[str, str] | None]] = []
        self.closed = False

    async def post(
        self, url: str, *, data: dict[str, str], auth: tuple[str, str] | None = None
    ) -> httpx.Response:
        """Capture POST data and return a configured response."""
        self.calls.append((url, data, auth))
        if self.raise_error is not None:
            raise self.raise_error
        request = httpx.Request("POST", url)
        return httpx.Response(self.status_code, request=request)

    async def aclose(self) -> None:
        """Mark the client as closed."""
        self.closed = True


def test_mailgun_requires_auth() -> None:
    """MailgunClient should require auth configuration."""
    with pytest.raises(MissingClientAuthError):
        MailgunClient(
            domain="example.com", sender_email="sender@example.com", sender_display_name="Sender"
        )


def test_mailgun_invalid_base_url() -> None:
    """MailgunClient should validate the base URL."""
    with pytest.raises(MalformedClientUrlError) as exc:
        MailgunClient(
            domain="example.com",
            sender_email="sender@example.com",
            sender_display_name="Sender",
            api_key="key",
            base_url="not-a-url",
        )

    assert exc.value.base_url == "not-a-url"


def test_mailgun_notify_missing_subject() -> None:
    """MailgunClient should reject missing subject when no default is set."""
    client = MailgunClient(
        domain="example.com",
        sender_email="sender@example.com",
        sender_display_name="Sender",
        api_key="key",
        http_client=cast("httpx.AsyncClient", FakeAsyncClient(auth=("api", "key"))),
    )
    content = NotificationContent(body="Hello", subject=None)

    with pytest.raises(EmailNotificationMissingSubjectError):
        asyncio.run(client.notify(content, recipient=cast("EmailAddress", "user@example.com")))


def test_mailgun_notify_invalid_recipient() -> None:
    """MailgunClient should validate recipient emails."""
    client = MailgunClient(
        domain="example.com",
        sender_email="sender@example.com",
        sender_display_name="Sender",
        api_key="key",
        http_client=cast("httpx.AsyncClient", FakeAsyncClient(auth=("api", "key"))),
        default_subject="Hello",
    )
    content = NotificationContent(body="Hello", subject=None)

    with pytest.raises(MalformedRecipientEmailError):
        asyncio.run(client.notify(content, recipient=cast("EmailAddress", "not-an-email")))


def test_mailgun_notify_uses_default_subject_and_auth() -> None:
    """MailgunClient should send notifications using default subject and auth."""
    fake_client = FakeAsyncClient(auth=None)
    client = MailgunClient(
        domain="example.com",
        sender_email="sender@example.com",
        sender_display_name="Sender",
        api_key="key",
        http_client=cast("httpx.AsyncClient", fake_client),
        default_subject="Default subject",
    )
    content = NotificationContent(body="Hello", subject=None)

    asyncio.run(client.notify(content, recipient=cast("EmailAddress", "user@example.com")))

    assert len(fake_client.calls) == 1
    url, data, auth = fake_client.calls[0]
    assert url.endswith("/example.com/messages")
    assert data["subject"] == "Default subject"
    assert data["text"] == "Hello"
    assert data["to"] == "user@example.com"
    assert data["from"] == "Sender <sender@example.com>"
    assert auth == ("api", "key")


def test_mailgun_notify_from_template() -> None:
    """MailgunClient should send template notifications with variables."""
    fake_client = FakeAsyncClient(auth=("api", "key"))
    client = MailgunClient(
        domain="example.com",
        sender_email="sender@example.com",
        sender_display_name="Sender",
        api_key="key",
        http_client=cast("httpx.AsyncClient", fake_client),
    )

    asyncio.run(
        client.notify_from_template(
            "welcome",
            recipient=cast("EmailAddress", "user@example.com"),
            version="v1",
            first_name="Ada",
        )
    )

    url, data, auth = fake_client.calls[0]
    assert url.endswith("/example.com/messages")
    assert data["template"] == "welcome"
    assert data["t:version"] == "v1"
    assert "Ada" in data["t:variables"]
    assert auth is None


def test_mailgun_post_error_wrapped() -> None:
    """MailgunClient should wrap HTTP errors in MailAPIError."""
    request = httpx.Request("POST", "https://api.example.com")
    error = httpx.ConnectError("boom", request=request)
    fake_client = FakeAsyncClient(auth=None, raise_error=error)
    client = MailgunClient(
        domain="example.com",
        sender_email="sender@example.com",
        sender_display_name="Sender",
        api_key="key",
        http_client=cast("httpx.AsyncClient", fake_client),
    )

    content = NotificationContent(body="Hello", subject="Subject")

    with pytest.raises(MailAPIError):
        asyncio.run(client.notify(content, recipient=cast("EmailAddress", "user@example.com")))
