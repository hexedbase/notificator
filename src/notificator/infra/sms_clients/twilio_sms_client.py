"""Twilio-backed SMS notification client implementation."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Annotated

import phonenumbers
from pydantic import TypeAdapter, ValidationError
from pydantic_extra_types.phone_numbers import PhoneNumber as PydanticPhoneNumber
from pydantic_extra_types.phone_numbers import PhoneNumberValidator
from twilio.base import values
from twilio.base.exceptions import TwilioException
from twilio.http.async_http_client import AsyncTwilioHttpClient
from twilio.rest import Client

from notificator.domain import AsyncClosable, NotificationClient, NotificationContent, PhoneNumber
from notificator.infra.sms_clients.exceptions import (
    InvalidPhoneNumberFormatError,
    SmsAPIError,
    TemplateNotProvidedError,
    TemplateVersionNotAvailableError,
    TwilioMissingSenderIdError,
)

if TYPE_CHECKING:
    from twilio.http import AsyncHttpClient

# Twilio requires phone numbers to be in E164 format while pydantic.PhoneNumber defaults to RFC3966
E164Number = Annotated[
    str | phonenumbers.PhoneNumber | PydanticPhoneNumber | PhoneNumber,
    PhoneNumberValidator(number_format="E164"),
]

_phone_number_adapter = TypeAdapter(E164Number)


@dataclass(frozen=True, slots=True)
class TwilioSmsTemplate:
    """Template metadata for Twilio Content API usage.

    Attributes:
        id: Twilio Content SID for the template or a friendly name if using registry anyway.
        version_registry: Optional mapping of friendly version names to Content SIDs.
    """

    id: str
    version_registry: dict[str, str] = field(default_factory=dict)


class TwilioSmsClient(NotificationClient[PhoneNumber], AsyncClosable):
    """Send SMS notifications via Twilio's REST API."""

    __slots__ = ("_client", "_messaging_service_sid", "_sender_phone_number", "_template_registry")

    def __init__(  # noqa: PLR0913
        self,
        account_sid: str,
        token: str,
        *,
        templates: list[TwilioSmsTemplate | str] | None = None,
        twilio_http_client: AsyncHttpClient | None = None,
        messaging_service_sid: str | None = None,
        sender_phone_number: PhoneNumber | None = None,
    ) -> None:
        """Initialize a Twilio-backed SMS notification client.

        Args:
            account_sid: Twilio account SID.
            token: Twilio auth token.
            templates: Optional list of templates, either str representing sid or
                TwilioSmsTemplate data objects, allowing custom versioning.
            twilio_http_client: Optional async HTTP client for Twilio.
            messaging_service_sid: Optional messaging service SID.
            sender_phone_number: Optional sender phone number in E.164 format.

        Raises:
            TwilioMissingSenderIdError: Raised when neither sender phone number nor
                messaging service SID is provided.
            InvalidPhoneNumberFormatError: Raised when `sender_phone_number` is invalid.
        """
        template_registry: dict[str, TwilioSmsTemplate] = {}

        if templates is not None:
            for t in templates:
                if isinstance(t, str):
                    template_registry[t] = TwilioSmsTemplate(id=t)
                else:
                    template_registry[t.id] = t

        if sender_phone_number is None and messaging_service_sid is None:
            raise TwilioMissingSenderIdError

        if sender_phone_number is not None:
            try:
                e164_sender_phone_number = _phone_number_adapter.validate_python(
                    sender_phone_number
                )
            except ValidationError as e:
                raise InvalidPhoneNumberFormatError(sender_phone_number) from e
        else:
            e164_sender_phone_number = None

        self._client = Client(
            account_sid, token, http_client=twilio_http_client or AsyncTwilioHttpClient()
        )
        self._messaging_service_sid = messaging_service_sid
        self._sender_phone_number = e164_sender_phone_number
        self._template_registry = template_registry

    def _validate_phone_number(self, phone_number: PhoneNumber) -> str:
        try:
            return _phone_number_adapter.validate_python(phone_number)
        except ValidationError as e:
            raise InvalidPhoneNumberFormatError(phone_number) from e

    async def aclose(self) -> None:
        """Close the underlying Twilio HTTP client if it is async-aware."""
        if isinstance(self._client.http_client, AsyncTwilioHttpClient):
            await self._client.http_client.close()

    async def notify(self, content: NotificationContent, *, recipient: PhoneNumber) -> None:
        """Send a plain SMS message to a recipient.

        Args:
            content: Notification payload containing the message body.
            recipient: E.164-compatible phone number to receive the SMS.
        """
        e164_recipient = self._validate_phone_number(recipient)

        try:
            await self._client.messages.create_async(
                from_=self._sender_phone_number or values.unset,
                messaging_service_sid=self._messaging_service_sid or values.unset,
                body=content.body,
                to=e164_recipient,
            )
        except TwilioException as e:
            raise SmsAPIError from e

    async def notify_from_template(
        self, template: str, *, recipient: PhoneNumber, version: str | None = None, **variables: str
    ) -> None:
        """Send a Twilio Content API template with injected variables.

        Args:
            template: Template identifier registered in Twilio.
            recipient: E.164-compatible phone number to receive the SMS.
            version: Optional template version alias or ID to resolve.
            **variables: Template variables to inject into the message.
        """
        e164_recipient = self._validate_phone_number(recipient)
        try:
            template_obj = self._template_registry[template]
        except KeyError as e:
            raise TemplateNotProvidedError(template) from e

        if version:
            try:
                version = template_obj.version_registry[version]
            except KeyError as e:
                raise TemplateVersionNotAvailableError(
                    template_name=template_obj.id, version=version
                ) from e
        try:
            variables_str = json.dumps(variables)
            await self._client.messages.create_async(
                from_=self._sender_phone_number or values.unset,
                messaging_service_sid=self._messaging_service_sid or values.unset,
                content_sid=template,
                content_variables=variables_str,
                to=e164_recipient,
            )
        except TwilioException as e:
            raise SmsAPIError from e
