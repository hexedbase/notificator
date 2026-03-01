"""Email delivery facades and exceptions."""

from __future__ import annotations

import importlib
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from collections.abc import Callable

    from notificator.infra.mail_clients.exceptions import (
        EmailNotificationMissingSubjectError,
        MailAPIError,
        MailNotificationError,
        MalformedClientUrlError,
        MalformedRecipientEmailError,
        MissingClientAuthError,
    )
    from notificator.infra.mail_clients.mailgun_client import MailgunClient


def _load_mailgun_client() -> object:
    module = importlib.import_module("notificator.infra.mail_clients.mailgun_client")
    return module.MailgunClient


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


_EXPORTS: Final[dict[str, Callable[[], object]]] = {
    "MailgunClient": _load_mailgun_client,
    "MailNotificationError": _load_mail_notification_error,
    "MalformedClientUrlError": _load_malformed_client_url_error,
    "MalformedRecipientEmailError": _load_malformed_recipient_email_error,
    "MissingClientAuthError": _load_missing_client_auth_error,
    "MailAPIError": _load_mail_api_error,
    "EmailNotificationMissingSubjectError": _load_email_notification_missing_subject_error,
}

__all__ = (
    "EmailNotificationMissingSubjectError",
    "MailAPIError",
    "MailNotificationError",
    "MailgunClient",
    "MalformedClientUrlError",
    "MalformedRecipientEmailError",
    "MissingClientAuthError",
)


def __getattr__(name: str) -> object:
    """Lazily load mail client classes and exceptions."""
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
