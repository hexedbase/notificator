# Templates

Templates let you store message structure on the provider side and only inject
variables at send time. This keeps formatting concerns out of application code and
makes it easy to update copy without a deployment.

Both `MailgunClient` and `TwilioSmsClient` expose a `notify_from_template()` method
that follows the same signature defined on `NotificationClient`.

## Mailgun templates

Mailgun templates are created in the Mailgun dashboard or via the Mailgun API and
are identified by name. Variables are passed as keyword arguments and serialized
to JSON before the request is sent.

```python
from notificator import EmailAddress
from notificator.mail import MailgunClient

client = MailgunClient(
    domain="mg.example.com",
    api_key="key-...",
    sender_email="no-reply@example.com",
    sender_display_name="My Service",
)

await client.notify_from_template(
    "order_shipped",                          # Mailgun template name
    recipient=EmailAddress("user@example.com"),
    order_id="ORD-1234",
    status="shipped",
    tracking_url="https://track.example.com/ORD-1234",
)
```

### Template versions

Mailgun supports versioned templates. Pass the version name as the `version` keyword:

```python
await client.notify_from_template(
    "order_shipped",
    recipient=EmailAddress("user@example.com"),
    version="v2",
    order_id="ORD-1234",
)
```

## Twilio Content API templates

Twilio templates use the [Content API](https://www.twilio.com/docs/content) and are
identified by a Content SID (e.g. `HXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`).

### Plain SID

If you only need one version per template, pass the Content SID as a plain string
when constructing the client:

```python
from notificator import PhoneNumber
from notificator.sms import TwilioSmsClient

client = TwilioSmsClient(
    account_sid="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    token="your_auth_token",
    sender_phone_number=PhoneNumber("+15551234567"),
    templates=["HXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"],
)

await client.notify_from_template(
    "HXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    recipient=PhoneNumber("+15557654321"),
    first_name="Ada",
    code="123456",
)
```

### Named templates with a version registry

`TwilioSmsTemplate` let's you assign a friendly name to a template and map
human-readable version aliases to their Content SIDs. This is useful when the same
logical template has locale variants or A/B versions stored as separate Content SIDs.

```python
from notificator.sms import TwilioSmsClient, TwilioSmsTemplate

shipping_template = TwilioSmsTemplate(
    id="order_shipped",                  # Friendly name used when calling notify_from_template
    version_registry={
        "en": "HXaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",   # English variant SID
        "pl": "HXbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",   # Polish variant SID
    },
)

client = TwilioSmsClient(
    account_sid="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    token="your_auth_token",
    sender_phone_number=PhoneNumber("+15551234567"),
    templates=[shipping_template],
)

# Send the Polish variant
await client.notify_from_template(
    "order_shipped",
    recipient=PhoneNumber("+15557654321"),
    version="pl",
    tracking_url="https://track.example.com/ORD-1234",
)
```

When `version` is provided, the client resolves the alias through `version_registry`
to get the actual Content SID before sending.

## Variable naming

Keep variable names consistent across templates to simplify integration code.
Prefer `snake_case` names to match Python conventions, since they are passed
directly as keyword arguments:

```python
# Consistent naming makes call sites predictable
await client.notify_from_template(
    "welcome",
    recipient=...,
    first_name="Ada",
    verification_link="https://...",
)
```

## Error handling

| Exception | When it is raised |
|---|---|
| `TemplateNotProvidedError` | `notify_from_template()` was called with a template name not registered on the client. |
| `TemplateVersionNotAvailableError` | The requested `version` alias is not in the template's `version_registry`. |

```python
from notificator.sms import TemplateNotProvidedError, TemplateVersionNotAvailableError

try:
    await client.notify_from_template("unknown_template", recipient=PhoneNumber("+15557654321"))
except TemplateNotProvidedError as e:
    print(f"Template '{e.template_name}' is not configured for this client.")
except TemplateVersionNotAvailableError as e:
    print(f"Version '{e.version}' not found for template '{e.template_name}'.")
```

!!! note
    These errors are raised locally before any network call is made, so they are
    cheap and safe to catch without retry logic.
