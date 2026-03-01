"""Notification exceptions facade."""

from __future__ import annotations

import importlib
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from collections.abc import Callable

    from notificator.domain.exceptions import NotificationError
    from notificator.infra.mail_clients.exceptions import (
        EmailNotificationMissingSubjectError,
        MailAPIError,
        MailNotificationError,
        MalformedClientUrlError,
        MalformedRecipientEmailError,
        MissingClientAuthError,
    )
    from notificator.infra.sms_clients.exceptions import (
        InvalidPhoneNumberFormatError,
        SmsAPIError,
        SmsNotificationError,
        TemplateNotProvidedError,
        TemplateVersionNotAvailableError,
        TwilioMissingSenderIdError,
    )


def _load_notification_error() -> object:
    module = importlib.import_module("notificator.domain.exceptions")
    return module.NotificationError


def _load_mail_notification_error() -> object:
    module = importlib.import_module("notificator.infra.mail_clients.exceptions")
    return module.MailNotificationError


def _load_malformed_client_url_error() -> object:
    module = importlib.import_module("notificator.infra.mail_clients.exceptions")
    return module.MalformedClientUrlError


def _load_malformed_recipient_email_error() -> object:
    module = importlib.import_module("notificator.infra.mail_clients.exceptions")
    return module.MalformedRecipientEmailError


def _load_missing_client_auth_error() -> object:
    module = importlib.import_module("notificator.infra.mail_clients.exceptions")
    return module.MissingClientAuthError


def _load_mail_api_error() -> object:
    module = importlib.import_module("notificator.infra.mail_clients.exceptions")
    return module.MailAPIError


def _load_email_notification_missing_subject_error() -> object:
    module = importlib.import_module("notificator.infra.mail_clients.exceptions")
    return module.EmailNotificationMissingSubjectError


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
    "NotificationError": _load_notification_error,
    "MailNotificationError": _load_mail_notification_error,
    "MalformedClientUrlError": _load_malformed_client_url_error,
    "MalformedRecipientEmailError": _load_malformed_recipient_email_error,
    "MissingClientAuthError": _load_missing_client_auth_error,
    "MailAPIError": _load_mail_api_error,
    "EmailNotificationMissingSubjectError": _load_email_notification_missing_subject_error,
    "SmsNotificationError": _load_sms_notification_error,
    "TwilioMissingSenderIdError": _load_twilio_missing_sender_id_error,
    "InvalidPhoneNumberFormatError": _load_invalid_phone_number_format_error,
    "SmsAPIError": _load_sms_api_error,
    "TemplateNotProvidedError": _load_template_not_provided_error,
    "TemplateVersionNotAvailableError": _load_template_version_not_available_error,
}

__all__ = (
    "EmailNotificationMissingSubjectError",
    "InvalidPhoneNumberFormatError",
    "MailAPIError",
    "MailNotificationError",
    "MalformedClientUrlError",
    "MalformedRecipientEmailError",
    "MissingClientAuthError",
    "NotificationError",
    "SmsAPIError",
    "SmsNotificationError",
    "TemplateNotProvidedError",
    "TemplateVersionNotAvailableError",
    "TwilioMissingSenderIdError",
)


def __getattr__(name: str) -> object:
    """Lazily load notification exceptions."""
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
