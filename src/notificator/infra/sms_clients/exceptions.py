"""Base module for sms clients exceptions."""

from notificator.domain.exceptions import NotificationError


class SmsNotificationError(NotificationError):
    """Base exception for sms notification errors."""


class TwilioMissingSenderIdError(SmsNotificationError):
    """Raised when a twilio client is missing a sender identity."""

    def __init__(self) -> None:
        super().__init__(
            "Twilio client is missing a sender identity. Either provide a valid `sender_phone_number` "
            "or a `messaging_service_sid`."
        )


class InvalidPhoneNumberFormatError(SmsNotificationError):
    """Raised when a phone number format is invalid for a client."""

    def __init__(self, phone_number: str, expected_format: str = "E164") -> None:
        self.phone_number = phone_number
        self.expected_format = expected_format
        super().__init__(
            f"Provided phone number {self.phone_number} does not match expected format: {self.expected_format}"
        )


class SmsAPIError(SmsNotificationError):
    """Exception raised when an error occurs while making an API call."""


class TemplateNotProvidedError(SmsNotificationError):
    """Raised when requested to use a template that is not available for this client."""

    def __init__(self, template_name: str) -> None:
        self.template_name = template_name
        super().__init__(f"Template {self.template_name} is not configured for this Sms client.")


class TemplateVersionNotAvailableError(SmsNotificationError):
    """Raised when a template version is not available."""

    def __init__(self, template_name: str, version: str) -> None:
        self.template_name = template_name
        self.version = version
        super().__init__(
            f"Version {self.version} is not available for template {self.template_name}."
        )
