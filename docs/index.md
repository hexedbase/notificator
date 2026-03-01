# Notificator

Notificator is a lightweight async Python library that unifies email and SMS delivery
behind a single, protocol-driven interface. It ships with adapters for **Mailgun** (email)
and **Twilio** (SMS) and is designed to be easy to test, easy to extend, and straightforward
to drop into any async Python service.

## Key features

| | |
|---|---|
| **Async-first** | Every delivery method is `async`, built on `httpx` and Twilio's async client. |
| **Protocol-based design** | `NotificationClient` is a structural `Protocol` — swap adapters or mock in tests without any patching. |
| **Unified payload** | `NotificationContent` is one frozen dataclass shared across every transport. |
| **Template delivery** | Send provider-stored templates with injected variables. Twilio supports named version registries. |
| **Type-safe recipients** | `EmailAddress` and `PhoneNumber` are `NewType` wrappers that let type checkers enforce the right recipient type per client. |

## Architecture

The library is layered so internal details never leak into call sites:

```
notificator/
├── domain/       # Protocols (NotificationClient, AsyncClosable), value objects, base exception
├── infra/        # Provider implementations: MailgunClient, TwilioSmsClient
├── mail/         # Public email facade — MailgunClient + mail exceptions
├── sms/          # Public SMS facade — TwilioSmsClient, TwilioSmsTemplate + SMS exceptions
├── abc/          # Public protocol facade — NotificationClient, AsyncClosable
└── exceptions/   # Unified exception facade covering all providers
```

Import from the root package or from the provider-specific facades:

```python
from notificator import NotificationContent, EmailAddress, PhoneNumber
from notificator.mail import MailgunClient
from notificator.sms import TwilioSmsClient, TwilioSmsTemplate
```

## Where to go next

- [Getting Started](getting-started.md) — install the package and send your first message.
- [Templates Guide](guides/templates.md) — use provider-stored templates with variable injection.
- [Provider Configuration](guides/providers.md) — full options for Mailgun and Twilio clients.
- [API Reference](reference.md) — auto-generated reference for all public classes and protocols.
