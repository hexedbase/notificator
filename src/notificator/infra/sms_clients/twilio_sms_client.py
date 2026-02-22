import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Annotated, NewType

import phonenumbers
from pydantic import TypeAdapter, ValidationError
from pydantic_extra_types.phone_numbers import PhoneNumberValidator
from twilio.base import values
from twilio.base.exceptions import TwilioException
from twilio.http.async_http_client import AsyncTwilioHttpClient
from twilio.rest import Client

from notificator.domain import AsyncClosable, NotificationClient, NotificationContent
from notificator.infra.sms_clients.exceptions import (
    InvalidPhoneNumberFormatError,
    SmsAPIError,
    TemplateNotProvidedError,
    TemplateVersionNotAvailableError,
    TwilioMissingSenderIdError,
)

if TYPE_CHECKING:
    from twilio.http import AsyncHttpClient

PhoneNumber = NewType("PhoneNumber", str)

E164NumberType = Annotated[
    str, phonenumbers.PhoneNumber, PhoneNumberValidator(number_format="E164")
]

_phone_number_adapter = TypeAdapter(E164NumberType)


@dataclass(frozen=True, slots=True)
class TwilioSmsTemplate:
    id: str
    version_registry: dict[str, str] = field(default_factory=dict)


class TwilioSmsClient(NotificationClient[PhoneNumber], AsyncClosable):
    __slots__ = ("_client", "_messaging_service_sid", "_sender_phone_number", "_templates")

    def __init__( # noqa: PLR0913
        self,
        account_sid: str,
        token: str,
        *,
        templates: list[TwilioSmsTemplate] | None = None,
        twilio_http_client: AsyncHttpClient | None = None,
        messaging_service_sid: str | None = None,
        sender_phone_number: PhoneNumber | None = None,
    ) -> None:
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
        self._template_registry = {t.id: t for t in templates} if templates else {}

    def _validate_phone_number(self, phone_number: PhoneNumber) -> str:
        try:
            return _phone_number_adapter.validate_python(phone_number)
        except ValidationError as e:
            raise InvalidPhoneNumberFormatError(phone_number) from e

    async def aclose(self) -> None:
        if isinstance(self._client.http_client, AsyncTwilioHttpClient):
            await self._client.http_client.close()

    async def notify(self, content: NotificationContent, *, recipient: PhoneNumber) -> None:
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
