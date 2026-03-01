"""Module containing static type markers used by notificator."""

from typing import NewType

EmailAddress = NewType("EmailAddress", str)

PhoneNumber = NewType("PhoneNumber", str)
