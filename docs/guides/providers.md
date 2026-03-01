# Provider Configuration

This guide covers all configuration options for `MailgunClient` and `TwilioSmsClient`,
along with the error hierarchy for each provider.

## Mailgun

`MailgunClient` sends email via the [Mailgun HTTP API](https://documentation.mailgun.com/).

### Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `domain` | `str` | Yes | Mailgun sending domain (e.g. `mg.example.com`). |
| `sender_email` | `str` | Yes | Email address used in the `From` header. |
| `sender_display_name` | `str` | Yes | Display name used in the `From` header. |
| `api_key` | `str \| None` | Conditionally | Mailgun API key. Required unless `http_client` is pre-authenticated. |
| `http_client` | `httpx.AsyncClient \| None` | Conditionally | Pre-configured async HTTP client. Use instead of `api_key` for custom auth or transport. |
| `base_url` | `str` | No | Mailgun API base URL. Defaults to the EU endpoint (`https://api.eu.mailgun.net/v3`). |
| `default_subject` | `str \| None` | No | Fallback subject for emails where `NotificationContent.subject` is not set. |

### Minimal example

```python
from notificator.mail import MailgunClient

client = MailgunClient(
    domain="mg.example.com",
    api_key="key-...",
    sender_email="no-reply@example.com",
    sender_display_name="My Service",
)
```

### US region

Mailgun hosts US customers on a different API endpoint. Override `base_url` if your
domain is registered in the US region:

```python
client = MailgunClient(
    domain="mg.example.com",
    api_key="key-...",
    sender_email="no-reply@example.com",
    sender_display_name="My Service",
    base_url="https://api.mailgun.net/v3",  # US region
)
```

### Custom HTTP client

Pass a pre-configured `httpx.AsyncClient` to control timeouts, proxies, or
connection pool settings. When using this option, either include auth in the
client or also pass `api_key`:

```python
import httpx
from notificator.mail import MailgunClient

http_client = httpx.AsyncClient(
    auth=("api", "key-..."),
    timeout=httpx.Timeout(10.0),
)

client = MailgunClient(
    domain="mg.example.com",
    sender_email="no-reply@example.com",
    sender_display_name="My Service",
    http_client=http_client,
)
```

### Error hierarchy

```
NotificationError
└── MailNotificationError
    ├── MissingClientAuthError      — neither api_key nor authenticated http_client provided
    ├── MalformedClientUrlError     — base_url is not a valid URL
    ├── MalformedRecipientEmailError — recipient is not a valid email address
    ├── EmailNotificationMissingSubjectError — no subject on content and no default_subject
    └── MailAPIError                — Mailgun API returned an HTTP error
```

Import exceptions from `notificator.mail` or from the unified `notificator.exceptions` facade:

```python
from notificator.mail import (
    MailAPIError,
    MalformedRecipientEmailError,
    EmailNotificationMissingSubjectError,
    MissingClientAuthError,
)
```

---

## Twilio

`TwilioSmsClient` sends SMS via the [Twilio REST API](https://www.twilio.com/docs/sms).

### Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `account_sid` | `str` | Yes | Twilio account SID. |
| `token` | `str` | Yes | Twilio auth token. |
| `sender_phone_number` | `PhoneNumber \| None` | Conditionally | Sender phone number in E.164 format. Required unless `messaging_service_sid` is provided. |
| `messaging_service_sid` | `str \| None` | Conditionally | Twilio Messaging Service SID. Use instead of `sender_phone_number` for number pools. |
| `templates` | `list[TwilioSmsTemplate \| str] \| None` | No | Templates available to this client instance. Plain strings are treated as Content SIDs. |
| `twilio_http_client` | `AsyncHttpClient \| None` | No | Custom Twilio async HTTP client for advanced transport control. |

### Minimal example (phone number sender)

```python
from notificator import PhoneNumber
from notificator.sms import TwilioSmsClient

client = TwilioSmsClient(
    account_sid="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    token="your_auth_token",
    sender_phone_number=PhoneNumber("+15551234567"),
)
```

### Messaging Service SID

Use a [Messaging Service](https://www.twilio.com/docs/messaging/services) SID instead
of a phone number to enable number pools, sticky sender, and other Twilio features:

```python
client = TwilioSmsClient(
    account_sid="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    token="your_auth_token",
    messaging_service_sid="MGxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
)
```

### Registering templates

Templates must be registered when constructing the client. Pass plain Content SIDs
or `TwilioSmsTemplate` objects:

```python
from notificator.sms import TwilioSmsClient, TwilioSmsTemplate

client = TwilioSmsClient(
    account_sid="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    token="your_auth_token",
    sender_phone_number=PhoneNumber("+15551234567"),
    templates=[
        "HXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",        # plain SID — template id == SID
        TwilioSmsTemplate(                           # named template with version aliases
            id="order_shipped",
            version_registry={
                "en": "HXaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                "pl": "HXbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            },
        ),
    ],
)
```

See [Templates](templates.md) for full details on versioned templates.

### Error hierarchy

```
NotificationError
└── SmsNotificationError
    ├── TwilioMissingSenderIdError       — neither sender_phone_number nor messaging_service_sid provided
    ├── InvalidPhoneNumberFormatError    — phone number is not valid E.164
    ├── TemplateNotProvidedError         — template name not registered on this client instance
    ├── TemplateVersionNotAvailableError — version alias not found in the template's version_registry
    └── SmsAPIError                      — Twilio API returned an error
```

Import exceptions from `notificator.sms` or from the unified `notificator.exceptions` facade:

```python
from notificator.sms import (
    SmsAPIError,
    InvalidPhoneNumberFormatError,
    TemplateNotProvidedError,
    TemplateVersionNotAvailableError,
    TwilioMissingSenderIdError,
)
```

---

## Credentials management

Never hard-code API keys or auth tokens in source code. Retrieve them at runtime from
your environment or secret manager:

```python
import os
from notificator.mail import MailgunClient

client = MailgunClient(
    domain=os.environ["MAILGUN_DOMAIN"],
    api_key=os.environ["MAILGUN_API_KEY"],
    sender_email=os.environ["MAILGUN_SENDER_EMAIL"],
    sender_display_name="My Service",
)
```

For containerised deployments, inject secrets via environment variables or a secrets
manager (AWS Secrets Manager, GCP Secret Manager, HashiCorp Vault, etc.) rather than
mounting secret files directly into the image.
