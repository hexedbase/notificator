# Templates

Notificator supports provider templates for reusable notification content.
Use templates when you want to keep message structure in the provider and only
inject variables at send time.

## Send From Template

```python
await client.notify_from_template(
    template="<TEMPLATE_ID>",
    recipient="user@example.com",
    order_id="1234",
    status="shipped",
)
```

## Template Versions

Some providers support template versioning. When available, pass `version`:

```python
await client.notify_from_template(
    template="<TEMPLATE_ID>",
    version="v2",
    recipient="+15557654321",
    first_name="Ada",
)
```

## Variable Naming

Keep variable names consistent across templates to simplify integration. When
possible, prefer snake_case names to match Python conventions.
