# API Reference

Auto-generated from source docstrings. All public symbols are importable from the
facades described below — you do not need to import from `notificator.domain` or
`notificator.infra` directly.

## Root package

The `notificator` root re-exports the domain primitives you need in every call site:

```python
from notificator import (
    AsyncClosable,
    EmailAddress,
    NotificationClient,
    NotificationContent,
    NotificationError,
    PhoneNumber,
)
```

::: notificator.domain.value_objects

::: notificator.domain.types

::: notificator.domain.ports

::: notificator.domain.exceptions

## Email — `notificator.mail`

```python
from notificator.mail import MailgunClient
```

::: notificator.infra.mail_clients.mailgun_client

::: notificator.infra.mail_clients.exceptions

## SMS — `notificator.sms`

```python
from notificator.sms import TwilioSmsClient, TwilioSmsTemplate
```

::: notificator.infra.sms_clients.twilio_sms_client

::: notificator.infra.sms_clients.exceptions
