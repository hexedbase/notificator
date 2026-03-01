# Getting Started

Notificator requires **Python 3.13+**.

## Installation

The package is distributed via a private GitHub Packages registry. You need a GitHub
personal access token with the `read:packages` scope.

=== "uv"

    ```sh
    uv pip install \
      --extra-index-url "https://<USERNAME>:<TOKEN>@pip.pkg.github.com/pyron-solutions/" \
      notificator
    ```

=== "pip (one-off)"

    ```sh
    pip install \
      --extra-index-url "https://<USERNAME>:<TOKEN>@pip.pkg.github.com/pyron-solutions/" \
      notificator
    ```

=== "pip (persistent)"

    ```sh
    pip config set global.extra-index-url \
      "https://<USERNAME>:<TOKEN>@pip.pkg.github.com/pyron-solutions/"
    pip install notificator
    ```

Replace `<USERNAME>` and `<TOKEN>` with your GitHub credentials.

## Send an email

Import `MailgunClient` from `notificator.mail` and `NotificationContent` from `notificator`:

```python
import asyncio

from notificator import EmailAddress, NotificationContent
from notificator.mail import MailgunClient


async def main() -> None:
    client = MailgunClient(
        domain="mg.example.com",
        api_key="key-...",
        sender_email="no-reply@example.com",
        sender_display_name="My Service",
        default_subject="Service Notification",
    )

    await client.notify(
        NotificationContent(body="Hello from Notificator!"),
        recipient=EmailAddress("user@example.com"),
    )
    await client.aclose()


asyncio.run(main())
```

!!! note "Subject resolution"
    `notify()` requires a subject. Provide it via `NotificationContent(subject=...)`, or
    set a `default_subject` on the client. If neither is supplied,
    `EmailNotificationMissingSubjectError` is raised before any network call is made.

## Send an SMS

Import `TwilioSmsClient` from `notificator.sms`:

```python
import asyncio

from notificator import NotificationContent, PhoneNumber
from notificator.sms import TwilioSmsClient


async def main() -> None:
    client = TwilioSmsClient(
        account_sid="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        token="your_auth_token",
        sender_phone_number=PhoneNumber("+15551234567"),
    )

    await client.notify(
        NotificationContent(body="Your verification code is 123456."),
        recipient=PhoneNumber("+15557654321"),
    )
    await client.aclose()


asyncio.run(main())
```

!!! note "Phone number format"
    Phone numbers must be in [E.164 format](https://en.wikipedia.org/wiki/E.164)
    (e.g. `+15551234567`). `InvalidPhoneNumberFormatError` is raised for any number
    that fails validation.

## Resource cleanup

Both clients hold open connections. Always call `aclose()` when done — use a `try/finally`
block to ensure it runs even if an error occurs:

```python
async def send(body: str) -> None:
    client = MailgunClient(...)
    try:
        await client.notify(NotificationContent(body=body), recipient=EmailAddress("user@example.com"))
    finally:
        await client.aclose()
```

## Error handling

All exceptions inherit from `NotificationError`, so you can catch at whatever level of
specificity you need:

```python
from notificator import NotificationError
from notificator.mail import MailAPIError, MalformedRecipientEmailError

try:
    await client.notify(content, recipient=EmailAddress("not-an-email"))
except MalformedRecipientEmailError as e:
    # Validation failed locally — no HTTP call was made
    print(f"Invalid address: {e.recipient}")
except MailAPIError:
    # The Mailgun API returned an error response
    print("Delivery failed — check Mailgun logs.")
except NotificationError:
    # Catch-all for any other notificator error
    raise
```

For a full breakdown of errors per provider, see [Provider Configuration](guides/providers.md).

## Next steps

- Use [provider templates](guides/templates.md) for pre-formatted messages with injected variables.
- Read [Provider Configuration](guides/providers.md) for all client options, including EU regions
  and custom HTTP clients.
