# Provider Configuration

This guide summarizes provider-specific requirements for Notificator clients.

## Mailgun

Required:

- `domain`
- `sender_email`
- `sender_display_name`
- One of:
  - `api_key`
  - `http_client` with configured auth

Optional:

- `default_subject`
- `base_url` (e.g., EU region)

## Twilio

Required:

- `account_sid`
- `token`
- One of:
  - `sender_phone_number`
  - `messaging_service_sid`

Optional:

- `templates` for content-based messages
- `twilio_http_client` for custom HTTP settings

## Environment Variables

For internal deployments, we recommend storing provider credentials in your
service's secret manager and injecting them at runtime.
