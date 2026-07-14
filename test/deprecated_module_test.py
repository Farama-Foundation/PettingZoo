import pytest

from pettingzoo import classic
from pettingzoo.utils.deprecated_module import DeprecatedEnv, RemovedEnv


def test_removed_env_raises_with_guidance():
    """Removed envs point the user somewhere, rather than looking like a typo."""
    with pytest.raises(RemovedEnv, match="gin_rummy was removed"):
        _ = classic.gin_rummy_v5


def test_unknown_env_raises_attribute_error():
    """An env that never existed under this module is a plain AttributeError."""
    with pytest.raises(AttributeError, match="cannot import name"):
        _ = classic.knights_archers_zombies_v11


def test_getattr_default_still_works():
    """Errors must stay AttributeErrors so getattr() defaults keep working."""
    assert getattr(classic, "not_an_env", "default") == "default"


def test_outdated_version_still_deprecated():
    """Superseded versions keep their existing 'use the newer one' behavior."""
    with pytest.raises(DeprecatedEnv, match="use tictactoe_v3 instead"):
        classic.tictactoe_v2.env()
