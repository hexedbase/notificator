"""Tests for the Twilio SMS client."""

import asyncio
import json
import secrets
from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar, cast
from unittest.mock import patch

import pytest
from twilio.base.exceptions import TwilioException
from twilio.http.async_http_client import AsyncTwilioHttpClient

from notificator.domain.value_objects import NotificationContent
from notificator.infra.sms_clients.exceptions import (
    InvalidPhoneNumberFormatError,
    SmsAPIError,
    TemplateNotProvidedError,
    TemplateVersionNotAvailableError,
    TwilioMissingSenderIdError,
)
from notificator.infra.sms_clients.twilio_sms_client import (
    PhoneNumber,
    TwilioSmsClient,
    TwilioSmsTemplate,
)

if TYPE_CHECKING:
    from twilio.http import AsyncHttpClient


def _token() -> str:
    """Return a non-sensitive token value for tests."""
    return secrets.token_hex(8)


@dataclass
class FakeTwilioMessages:
    """Capture Twilio message create calls."""

    raise_error: bool = False
    last_kwargs: dict[str, object] | None = None

    async def create_async(self, **kwargs: object) -> None:
        """Capture Twilio message payload or raise an error."""
        if self.raise_error:
            message = "boom"
            raise TwilioException(message)
        self.last_kwargs = kwargs


class FakeTwilioClient:
    """Fake Twilio REST client."""

    last_instance: ClassVar[object | None] = None

    def __init__(self, account_sid: str, token: str, http_client: object) -> None:
        """Store http client and expose messages."""
        self.account_sid = account_sid
        self.token = token
        self.http_client = http_client
        self.messages = FakeTwilioMessages()
        FakeTwilioClient.last_instance = self


def test_twilio_requires_sender_id() -> None:
    """TwilioSmsClient should require a sender identifier."""
    with pytest.raises(TwilioMissingSenderIdError):
        TwilioSmsClient(account_sid="sid", token=_token())


def test_twilio_invalid_sender_phone_number() -> None:
    """TwilioSmsClient should validate sender phone numbers."""
    with pytest.raises(InvalidPhoneNumberFormatError):
        TwilioSmsClient(
            account_sid="sid",
            token=_token(),
            sender_phone_number=cast("PhoneNumber", "not-a-number"),
        )


def test_twilio_notify_success() -> None:
    """TwilioSmsClient should send SMS messages."""
    with patch("notificator.infra.sms_clients.twilio_sms_client.Client", FakeTwilioClient):
        dummy_http_client = cast("AsyncHttpClient", object())
        client = TwilioSmsClient(
            account_sid="sid",
            token=_token(),
            sender_phone_number=cast("PhoneNumber", "+14155552671"),
            twilio_http_client=dummy_http_client,
        )
        content = NotificationContent(body="Hello")

        asyncio.run(client.notify(content, recipient=cast("PhoneNumber", "+14155559999")))

        instance = cast("FakeTwilioClient", FakeTwilioClient.last_instance)
        assert instance is not None
        assert instance.messages.last_kwargs is not None
        assert instance.messages.last_kwargs["from_"] == "+14155552671"
        assert instance.messages.last_kwargs["to"] == "+14155559999"
        assert instance.messages.last_kwargs["body"] == "Hello"


def test_twilio_notify_invalid_recipient() -> None:
    """TwilioSmsClient should validate recipient phone numbers."""
    with patch("notificator.infra.sms_clients.twilio_sms_client.Client", FakeTwilioClient):
        dummy_http_client = cast("AsyncHttpClient", object())
        client = TwilioSmsClient(
            account_sid="sid",
            token=_token(),
            sender_phone_number=cast("PhoneNumber", "+14155552671"),
            twilio_http_client=dummy_http_client,
        )
        content = NotificationContent(body="Hello")

        with pytest.raises(InvalidPhoneNumberFormatError):
            asyncio.run(client.notify(content, recipient=cast("PhoneNumber", "bad-number")))


def test_twilio_notify_wraps_api_errors() -> None:
    """TwilioSmsClient should wrap Twilio errors as SmsAPIError."""

    class ErrorTwilioClient(FakeTwilioClient):
        """Fake Twilio client that always raises an error."""

        def __init__(self, account_sid: str, token: str, http_client: object) -> None:
            """Initialize the client with an erroring message sender."""
            super().__init__(account_sid, token, http_client)
            self.messages.raise_error = True

    with patch("notificator.infra.sms_clients.twilio_sms_client.Client", ErrorTwilioClient):
        dummy_http_client = cast("AsyncHttpClient", object())
        client = TwilioSmsClient(
            account_sid="sid",
            token=_token(),
            sender_phone_number=cast("PhoneNumber", "+14155552671"),
            twilio_http_client=dummy_http_client,
        )
        content = NotificationContent(body="Hello")

        with pytest.raises(SmsAPIError):
            asyncio.run(client.notify(content, recipient=cast("PhoneNumber", "+14155559999")))


def test_twilio_template_not_provided() -> None:
    """TwilioSmsClient should error when a template is missing."""
    with patch("notificator.infra.sms_clients.twilio_sms_client.Client", FakeTwilioClient):
        dummy_http_client = cast("AsyncHttpClient", object())
        client = TwilioSmsClient(
            account_sid="sid",
            token=_token(),
            sender_phone_number=cast("PhoneNumber", "+14155552671"),
            templates=[],
            twilio_http_client=dummy_http_client,
        )

        with pytest.raises(TemplateNotProvidedError):
            asyncio.run(
                client.notify_from_template(
                    "missing", recipient=cast("PhoneNumber", "+14155559999")
                )
            )


def test_twilio_template_version_not_available() -> None:
    """TwilioSmsClient should error when a version is missing."""
    with patch("notificator.infra.sms_clients.twilio_sms_client.Client", FakeTwilioClient):
        dummy_http_client = cast("AsyncHttpClient", object())
        client = TwilioSmsClient(
            account_sid="sid",
            token=_token(),
            sender_phone_number=cast("PhoneNumber", "+14155552671"),
            templates=[TwilioSmsTemplate(id="welcome", version_registry={})],
            twilio_http_client=dummy_http_client,
        )

        with pytest.raises(TemplateVersionNotAvailableError):
            asyncio.run(
                client.notify_from_template(
                    "welcome", recipient=cast("PhoneNumber", "+14155559999"), version="v1"
                )
            )


def test_twilio_notify_from_template() -> None:
    """TwilioSmsClient should send content API templates."""
    with patch("notificator.infra.sms_clients.twilio_sms_client.Client", FakeTwilioClient):
        template = TwilioSmsTemplate(id="welcome", version_registry={"v1": "sid-1"})
        dummy_http_client = cast("AsyncHttpClient", object())
        client = TwilioSmsClient(
            account_sid="sid",
            token=_token(),
            sender_phone_number=cast("PhoneNumber", "+14155552671"),
            templates=[template],
            twilio_http_client=dummy_http_client,
        )

        asyncio.run(
            client.notify_from_template(
                "welcome",
                recipient=cast("PhoneNumber", "+14155559999"),
                version="v1",
                first_name="Ada",
            )
        )

        instance = cast("FakeTwilioClient", FakeTwilioClient.last_instance)
        assert instance is not None
        assert instance.messages.last_kwargs is not None
        assert instance.messages.last_kwargs["content_sid"] == "welcome"
        assert instance.messages.last_kwargs["to"] == "+14155559999"
        variables = json.loads(cast("str", instance.messages.last_kwargs["content_variables"]))
        assert variables["first_name"] == "Ada"


def test_twilio_aclose_closes_async_http_client() -> None:
    """TwilioSmsClient should close async HTTP clients."""

    class DummyAsyncTwilioHttpClient(AsyncTwilioHttpClient):
        """Async HTTP client that tracks close calls."""

        def __init__(self) -> None:
            """Initialize the dummy async client."""
            self.closed = False

        async def close(self) -> None:
            """Mark the client as closed."""
            self.closed = True

    with patch("notificator.infra.sms_clients.twilio_sms_client.Client", FakeTwilioClient):
        http_client = DummyAsyncTwilioHttpClient()
        client = TwilioSmsClient(
            account_sid="sid",
            token=_token(),
            sender_phone_number=cast("PhoneNumber", "+14155552671"),
            twilio_http_client=http_client,
        )

        asyncio.run(client.aclose())
        assert http_client.closed is True
