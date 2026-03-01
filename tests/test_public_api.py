"""Tests for package public APIs."""

import importlib


def test_domain_public_api_exports() -> None:
    """Domain package should expose the expected public API."""
    module = importlib.import_module("notificator.domain")

    assert sorted(module.__all__) == sorted(
        ["AsyncClosable", "NotificationClient", "NotificationContent", "NotificationError"]
    )


def test_mail_clients_public_api_exports() -> None:
    """Mail clients package should expose the expected public API."""
    module = importlib.import_module("notificator.infra.mail_clients")

    assert sorted(module.__all__) == sorted(
        [
            "EmailNotificationMissingSubjectError",
            "MailAPIError",
            "MailgunClient",
            "MalformedRecipientEmailError",
            "MissingClientAuthError",
        ]
    )


def test_sms_clients_public_api_exports() -> None:
    """SMS clients package should expose the expected public API."""
    module = importlib.import_module("notificator.infra.sms_clients")

    assert sorted(module.__all__) == sorted(
        [
            "InvalidPhoneNumberFormatError",
            "SmsAPIError",
            "SmsNotificationError",
            "TemplateNotProvidedError",
            "TemplateVersionNotAvailableError",
            "TwilioMissingSenderIdError",
            "TwilioSmsClient",
            "TwilioSmsTemplate",
        ]
    )
