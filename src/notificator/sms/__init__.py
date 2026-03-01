"""SMS delivery facades and exceptions."""

from __future__ import annotations

import importlib
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from collections.abc import Callable

    from notificator.infra.sms_clients.exceptions import (
        InvalidPhoneNumberFormatError,
        SmsAPIError,
        SmsNotificationError,
        TemplateNotProvidedError,
        TemplateVersionNotAvailableError,
        TwilioMissingSenderIdError,
    )
    from notificator.infra.sms_clients.twilio_sms_client import TwilioSmsClient, TwilioSmsTemplate


def _load_twilio_sms_client() -> object:
    module = importlib.import_module("notificator.infra.sms_clients.twilio_sms_client")
    return module.TwilioSmsClient


def _load_twilio_sms_template() -> object:
    module = importlib.import_module("notificator.infra.sms_clients.twilio_sms_client")
    return module.TwilioSmsTemplate


def _load_sms_notification_error() -> object:
    module = importlib.import_module("notificator.infra.sms_clients.exceptions")
    return module.SmsNotificationError


def _load_twilio_missing_sender_id_error() -> object:
    module = importlib.import_module("notificator.infra.sms_clients.exceptions")
    return module.TwilioMissingSenderIdError


def _load_invalid_phone_number_format_error() -> object:
    module = importlib.import_module("notificator.infra.sms_clients.exceptions")
    return module.InvalidPhoneNumberFormatError


def _load_sms_api_error() -> object:
    module = importlib.import_module("notificator.infra.sms_clients.exceptions")
    return module.SmsAPIError


def _load_template_not_provided_error() -> object:
    module = importlib.import_module("notificator.infra.sms_clients.exceptions")
    return module.TemplateNotProvidedError


def _load_template_version_not_available_error() -> object:
    module = importlib.import_module("notificator.infra.sms_clients.exceptions")
    return module.TemplateVersionNotAvailableError


_EXPORTS: Final[dict[str, Callable[[], object]]] = {
    "TwilioSmsClient": _load_twilio_sms_client,
    "TwilioSmsTemplate": _load_twilio_sms_template,
    "SmsNotificationError": _load_sms_notification_error,
    "TwilioMissingSenderIdError": _load_twilio_missing_sender_id_error,
    "InvalidPhoneNumberFormatError": _load_invalid_phone_number_format_error,
    "SmsAPIError": _load_sms_api_error,
    "TemplateNotProvidedError": _load_template_not_provided_error,
    "TemplateVersionNotAvailableError": _load_template_version_not_available_error,
}

__all__ = (
    "InvalidPhoneNumberFormatError",
    "SmsAPIError",
    "SmsNotificationError",
    "TemplateNotProvidedError",
    "TemplateVersionNotAvailableError",
    "TwilioMissingSenderIdError",
    "TwilioSmsClient",
    "TwilioSmsTemplate",
)


def __getattr__(name: str) -> object:
    """Lazily load SMS client classes and exceptions."""
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
