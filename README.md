from notificator import EmailAddress[![Test](https://github.com/pyron-solutions/notificator/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/pyron-solutions/notificator/actions/workflows/test.yml) [![Coverage](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pyron-solutions/notificator/main/.github/badges/coverage.json)](https://github.com/pyron-solutions/notificator/actions/workflows/test.yml) [![Open in Dev Containers](https://img.shields.io/static/v1?label=Dev%20Containers&message=Open&color=blue&logo=data:image/svg%2bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0iI2ZmZiIgZD0iTTE3IDE2VjdsLTYgNU0yIDlWOGwxLTFoMWw0IDMgOC04aDFsNCAyIDEgMXYxNGwtMSAxLTQgMmgtMWwtOC04LTQgM0gzbC0xLTF2LTFsMy0zIi8+PC9zdmc+)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/pyron-solutions/notificator) [![Open in GitHub Codespaces](https://img.shields.io/static/v1?label=GitHub%20Codespaces&message=Open&color=blue&logo=github)](https://github.com/codespaces/new/pyron-solutions/notificator) [![Documentation](https://img.shields.io/static/v1?label=Documentation&message=View&color=blue&logo=readme&logoColor=white)](https://pyron-solutions.github.io/notificator)

# Notificator

A developer-friendly package for simplified notification management across internal
services. It provides a small domain model and async provider clients for sending
email and SMS.

## What It Provides

- Async notification clients for email (Mailgun) and SMS (Twilio).
- A shared `NotificationContent` value object for payload consistency.
- A `NotificationClient` protocol to make adapters testable and swappable.
- Template and non-template delivery workflows.

## Getting Started

### Install From Private GitHub Registry

1. Create a GitHub token with `read:packages`.
2. Configure your Python package manager to use the private registry.

`pip` (one-off install):

```sh
pip install \
  --extra-index-url "https://<USERNAME>:<TOKEN>@pip.pkg.github.com/pyron-solutions/" \
  notificator
```

`pip` (persistent config):

```sh
pip config set global.extra-index-url "https://<USERNAME>:<TOKEN>@pip.pkg.github.com/pyron-solutions/"
pip install notificator
```

`uv`:

```sh
uv pip install \
  --extra-index-url "https://<USERNAME>:<TOKEN>@pip.pkg.github.com/pyron-solutions/" \
  notificator
```

Replace `<USERNAME>` and `<TOKEN>` with your credentials.

### Quickstart: Mailgun Email

```python
import asyncio

from notificator import NotificationContent, EmailAddress
from notificator.mail import MailgunClient


async def main() -> None:
    mailing_client = MailgunClient(
        domain="<MAILGUN_DOMAIN>",
        api_key="<MAILGUN_API_KEY>",
        sender_email=EmailAddress("no-reply@<YOUR_DOMAIN>"),
        sender_display_name="Notificator",
        default_subject="Service Notification",
    )

    await mailing_client.notify(
        NotificationContent(body="Hello from Notificator!"),
        recipient=EmailAddress("user@example.com"),
    )
    await mailing_client.aclose()


asyncio.run(main())
```

### Quickstart: Twilio SMS

```python
import asyncio

from notificator import NotificationContent, PhoneNumber
from notificator.sms import TwilioSmsClient, TwilioSmsTemplate


async def main() -> None:
    template_with_custom_versioning = TwilioSmsTemplate(
       id="shipping_status_template",  # Friendly name
       version_registry={"en": "temp123_1", "pl": "temp123_2"}  # Friendly version name -> sid mapping
    )
    sms_client = TwilioSmsClient(
        account_sid="<TWILIO_ACCOUNT_SID>",
        token="<TWILIO_AUTH_TOKEN>",
        sender_phone_number=PhoneNumber("+15551234567"),
        templates=["temp_123_3", template_with_custom_versioning], # One plain template + a versioned template
    )

    await sms_client.notify(
        NotificationContent(body="Your verification code is 123456."),
        recipient=PhoneNumber("+15557654321"),
    )
    
    await sms_client.notify_from_template(
       template="shipping_status_template",
       recipient=PhoneNumber("+15557654321"),
       version="en",
       status="shipped",
       shipping_date="2026-03-01"
    )
    await sms_client.aclose()

asyncio.run(main())
```

### Template Delivery

```python
await mailing_client.notify_from_template(
    template="shipping_status_template",
    recipient=EmailAddress("user@example.com"),
    order_id="1234",
    status="shipped",
)
```

## Documentation

- Build docs: `poe docs`
- Serve docs locally: `poe docs --serve`
- API reference is generated via `mkdocstrings`.

## Linting

Run `poe lint` to apply formatting and ensure docstrings and typing checks pass.

## Contributing

<details>
<summary>Prerequisites</summary>

1. [Generate an SSH key](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent#generating-a-new-ssh-key) and [add the SSH key to your GitHub account](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account).
1. Configure SSH to automatically load your SSH keys:

    ```sh
    cat << EOF >> ~/.ssh/config
    
    Host *
      AddKeysToAgent yes
      IgnoreUnknown UseKeychain
      UseKeychain yes
      ForwardAgent yes
    EOF
    ```

1. [Install Docker Desktop](https://www.docker.com/get-started).
1. [Install VS Code](https://code.visualstudio.com/) and [VS Code's Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers). Alternatively, install [PyCharm](https://www.jetbrains.com/pycharm/download/).
1. _Optional:_ install a [Nerd Font](https://www.nerdfonts.com/font-downloads) such as [FiraCode Nerd Font](https://github.com/ryanoasis/nerd-fonts/tree/master/patched-fonts/FiraCode) and [configure VS Code](https://github.com/tonsky/FiraCode/wiki/VS-Code-Instructions) or [PyCharm](https://github.com/tonsky/FiraCode/wiki/Intellij-products-instructions) to use it.

</details>

<details open>
<summary>Development environments</summary>

The following development environments are supported:

1. ⭐️ _GitHub Codespaces_: click on [Open in GitHub Codespaces](https://github.com/codespaces/new/pyron-solutions/notificator) to start developing in your browser.
1. ⭐️ _VS Code Dev Container (with container volume)_: click on [Open in Dev Containers](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/pyron-solutions/notificator) to clone this repository in a container volume and create a Dev Container with VS Code.
1. ⭐️ _uv_: clone this repository and run the following from root of the repository:

    ```sh
    # Create and install a virtual environment
    uv sync --python 3.14 --all-extras

    # Activate the virtual environment
    source .venv/bin/activate

    # Install the pre-commit hooks
    pre-commit install --install-hooks
    ```

1. _VS Code Dev Container_: clone this repository, open it with VS Code, and run <kbd>Ctrl/⌘</kbd> + <kbd>⇧</kbd> + <kbd>P</kbd> → _Dev Containers: Reopen in Container_.
1. _PyCharm Dev Container_: clone this repository, open it with PyCharm, [create a Dev Container with Mount Sources](https://www.jetbrains.com/help/pycharm/start-dev-container-inside-ide.html), and [configure an existing Python interpreter](https://www.jetbrains.com/help/pycharm/configuring-python-interpreter.html#widget) at `/opt/venv/bin/python`.

</details>

<details open>
<summary>Developing</summary>

- This project follows the [Conventional Commits](https://www.conventionalcommits.org/) standard to automate [Semantic Versioning](https://semver.org/) and [Keep A Changelog](https://keepachangelog.com/) with [Commitizen](https://github.com/commitizen-tools/commitizen).
- Run `poe` from within the development environment to print a list of [Poe the Poet](https://github.com/nat-n/poethepoet) tasks available to run on this project.
- Run `uv add {package}` from within the development environment to install a run time dependency and add it to `pyproject.toml` and `uv.lock`. Add `--dev` to install a development dependency.
- Run `uv sync --upgrade` from within the development environment to upgrade all dependencies to the latest versions allowed by `pyproject.toml`. Add `--only-dev` to upgrade the development dependencies only.
- Run `cz bump` to bump the package's version, update the `CHANGELOG.md`, and create a git tag. Then push the changes and the git tag with `git push origin main --tags`.

</details>
