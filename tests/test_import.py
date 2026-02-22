"""Test Notificator."""

import notificator


def test_import() -> None:
    """Test that the package can be imported."""
    assert isinstance(notificator.__name__, str)
