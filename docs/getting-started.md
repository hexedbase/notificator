# Getting Started

Notificator requires Python 3.13+.

## Install From Private GitHub Registry

1. Create a GitHub token with `read:packages`.
2. Configure your Python package manager to use the private registry.

`pip` (one-off install):

```sh
pip install \
  --extra-index-url "https://<USERNAME>:<TOKEN>@pip.pkg.github.com/<ORG>/" \
  notificator
```

`pip` (persistent config):

```sh
pip config set global.extra-index-url "https://<USERNAME>:<TOKEN>@pip.pkg.github.com/<ORG>/"
pip install notificator
```

`uv`:

```sh
uv pip install \
  --extra-index-url "https://<USERNAME>:<TOKEN>@pip.pkg.github.com/<ORG>/" \
  notificator
```

Replace `<USERNAME>`, `<TOKEN>`, and `<ORG>` with your organization details.
If you use GitHub Enterprise, substitute `pip.pkg.github.com` with your internal
package host.

## Quickstart: Mailgun Email

```python
import asyncio

from notificator.domain import NotificationContent
from notificator.infra.mail_clients import MailgunClient


async def main() -> None:
    client = MailgunClient(
        domain="<MAILGUN_DOMAIN>",
        api_key="<MAILGUN_API_KEY>",
        sender_email="no-reply@<YOUR_DOMAIN>",
        sender_display_name="Notificator",
        default_subject="Service Notification",
    )

    await client.notify(
        NotificationContent(body="Hello from Notificator!"),
        recipient="user@example.com",
    )
    await client.aclose()


asyncio.run(main())
```

## Quickstart: Twilio SMS

```python
import asyncio

from notificator.domain import NotificationContent
from notificator.infra.sms_clients import TwilioSmsClient, TwilioSmsTemplate


async def main() -> None:
    client = TwilioSmsClient(
        account_sid="<TWILIO_ACCOUNT_SID>",
        token="<TWILIO_AUTH_TOKEN>",
        sender_phone_number="+15551234567",
        templates=[TwilioSmsTemplate(id="<TWILIO_CONTENT_SID>")],
    )

    await client.notify(
        NotificationContent(body="Your verification code is 123456."),
        recipient="+15557654321",
    )
    await client.aclose()


asyncio.run(main())
```
