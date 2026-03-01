"""Mailgun-backed email notification client implementation."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import httpx
from pydantic import AnyHttpUrl, EmailStr, TypeAdapter, ValidationError

from notificator import AsyncClosable
from notificator.domain import EmailAddress, NotificationClient
from notificator.infra.mail_clients.exceptions import (
    EmailNotificationMissingSubjectError,
    MailAPIError,
    MalformedClientUrlError,
    MalformedRecipientEmailError,
    MissingClientAuthError,
)

if TYPE_CHECKING:
    from notificator.domain.value_objects import NotificationContent

_email_adapter = TypeAdapter(EmailStr)
_http_url_adapter = TypeAdapter(AnyHttpUrl)


class MailgunClient(NotificationClient[EmailAddress], AsyncClosable):
    """Send email notifications via the Mailgun HTTP API."""

    __slots__ = (
        "_api_key",
        "_base_url",
        "_domain",
        "_http_client",
        "_sender_display_name",
        "_sender_email",
        "default_subject",
    )

    def __init__(  # noqa: PLR0913
        self,
        domain: str,
        *,
        default_subject: str | None = None,
        api_key: str | None = None,
        base_url: str = "https://api.eu.mailgun.net/v3",
        sender_email: str,
        sender_display_name: str,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        """Initialize a Mailgun-backed notification client.

        Args:
            domain: Mailgun domain used to send messages.
            default_subject: Default subject line for emails without an explicit subject.
            api_key: Mailgun API key. Optional if `http_client` already has auth.
            base_url: Mailgun API base URL.
            sender_email: Email address used in the From header.
            sender_display_name: Display name used in the From header.
            http_client: Optional preconfigured `httpx.AsyncClient`.

        Raises:
            MissingClientAuthError: Raised when neither `api_key` nor authenticated
                `http_client` is provided.
            MalformedClientUrlError: Raised when `base_url` is not a valid URL.
        """
        if api_key is None and (http_client is None or http_client.auth is None):
            raise MissingClientAuthError

        try:
            normalized_url = _http_url_adapter.validate_python(base_url)
        except ValidationError as e:
            raise MalformedClientUrlError(base_url) from e

        self.default_subject = default_subject

        self._api_key = api_key
        self._base_url = str(normalized_url)
        self._domain = domain
        self._http_client = (
            http_client or httpx.AsyncClient(auth=("api", self._api_key))
            if self._api_key
            else httpx.AsyncClient()
        )
        self._sender_email = sender_email
        self._sender_display_name = sender_display_name

    async def aclose(self) -> None:
        """Explicitly close the HTTP client to prevent connection leaks."""
        await self._http_client.aclose()

    def _validate_email(self, recipient: EmailAddress) -> str:
        try:
            return _email_adapter.validate_python(recipient)
        except ValidationError as e:
            raise MalformedRecipientEmailError(recipient) from e

    async def _post(self, data: dict[str, str]) -> None:
        url = f"{self._base_url}/{self._domain}/messages"

        try:
            if self._http_client.auth is None:
                assert self._api_key is not None, (
                    "this should never happen and is likely a bug, please report it."
                )
                auth = ("api", self._api_key)
                response = await self._http_client.post(url, data=data, auth=auth)
            else:
                response = await self._http_client.post(url, data=data)
            response.raise_for_status()
        except httpx.HTTPError as e:
            raise MailAPIError from e

    async def notify_from_template(
        self,
        template: str,
        *,
        recipient: EmailAddress,
        version: str | None = None,
        **variables: str,
    ) -> None:
        """Send a Mailgun template-based email to a recipient.

        Args:
            template: Mailgun template name.
            recipient: Email address to receive the notification.
            version: Optional Mailgun template version.
            **variables: Template variables to interpolate.
        """
        valid_email = self._validate_email(recipient)

        data = {
            "from": f"{self._sender_display_name} <{self._sender_email}>",
            "to": valid_email,
            "template": template,
            "t:variables": json.dumps(variables),
        }
        if version:
            data["t:version"] = version

        await self._post(data)

    async def notify(self, content: NotificationContent, *, recipient: EmailAddress) -> None:
        """Send a plain email notification without templates.

        Args:
            content: Notification payload with body and optional subject.
            recipient: Email address to receive the notification.
        """
        if content.subject is None and self.default_subject is None:
            raise EmailNotificationMissingSubjectError

        valid_email = self._validate_email(recipient)

        data: dict[str, str] = {
            "from": f"{self._sender_display_name} <{self._sender_email}>",
            "to": valid_email,
            "subject": content.subject
            or self.default_subject
            or "New Notification",  # Only to satisfy mypy
            "text": content.body,
        }

        await self._post(data)
