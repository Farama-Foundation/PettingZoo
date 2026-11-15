import pettingzoo.utils.wrappers as legacy_wrappers
from pettingzoo import utils as legacy_utils
from pettingzoo import wrappers


def test_public_wrapper_namespace_reexports_legacy_wrappers():
    assert wrappers.__all__ == legacy_wrappers.__all__
    for name in legacy_wrappers.__all__:
        assert getattr(wrappers, name) is getattr(legacy_wrappers, name)

    for name in legacy_wrappers.__all__:
        if hasattr(legacy_utils, name):
            assert getattr(wrappers, name) is getattr(legacy_utils, name)
