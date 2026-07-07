"""Tests for the PettingZoo registry (register/make/spec)."""

import pytest

from pettingzoo.env_registry.exceptions import (
    NameNotFound,
    NamespaceNotFound,
    VersionNotFound,
)
from pettingzoo.env_registry.registration import (
    EnvSpec,
    _get_env_id,
    _parse_env_id,
    aec_registry,
    find_spec,
    make,
    parallel_registry,
    register,
    spec,
)
from pettingzoo.utils.env import AECEnv, ParallelEnv


class TestParseEnvId:
    def test_simple_name_with_version(self):
        ns, name, version = _parse_env_id("CartPole-v1")
        assert ns is None
        assert name == "CartPole"
        assert version == 1

    def test_namespaced_with_version(self):
        ns, name, version = _parse_env_id("classic/rps-v2")
        assert ns == "classic"
        assert name == "rps"
        assert version == 2

    def test_no_version(self):
        ns, name, version = _parse_env_id("classic/rps")
        assert ns == "classic"
        assert name == "rps"
        assert version is None

    def test_underscore_in_name(self):
        ns, name, version = _parse_env_id("atari/space_invaders-v2")
        assert ns == "atari"
        assert name == "space_invaders"
        assert version == 2

    def test_no_namespace_no_version(self):
        ns, name, version = _parse_env_id("MyEnv")
        assert ns is None
        assert name == "MyEnv"
        assert version is None


class TestGetEnvId:
    def test_full(self):
        assert _get_env_id("classic", "rps", 2) == "classic/rps-v2"

    def test_no_namespace(self):
        assert _get_env_id(None, "rps", 2) == "rps-v2"

    def test_no_version(self):
        assert _get_env_id("classic", "rps", None) == "classic/rps"


class TestEnvSpec:
    def test_post_init_parsing(self):
        s = EnvSpec(id="classic/rps-v2", entry_point="some.module:func")
        assert s.namespace == "classic"
        assert s.name == "rps"
        assert s.version == 2


class TestRegister:
    def test_register_aec(self):
        register("aec", "test_ns/TestEnv-v0", entry_point="fake.module:env")
        assert "test_ns/TestEnv-v0" in aec_registry
        # cleanup
        del aec_registry["test_ns/TestEnv-v0"]

    def test_register_parallel(self):
        register(
            "parallel", "test_ns/TestEnv-v0", entry_point="fake.module:parallel_env"
        )
        assert "test_ns/TestEnv-v0" in parallel_registry
        del parallel_registry["test_ns/TestEnv-v0"]

    def test_register_warns_on_override(self):
        register("aec", "test_ns/Override-v0", entry_point="a:b")
        with pytest.warns(UserWarning, match="Overriding"):
            register("aec", "test_ns/Override-v0", entry_point="c:d")
        del aec_registry["test_ns/Override-v0"]

    def test_register_with_kwargs(self):
        register("aec", "test_ns/KW-v1", entry_point="a:b", kwargs={"x": 1})
        assert aec_registry["test_ns/KW-v1"].kwargs == {"x": 1}
        del aec_registry["test_ns/KW-v1"]


class TestVersionResolution:
    def setup_method(self):
        register("aec", "test_ns/VersionedEnv-v1", entry_point="a:b")
        register("aec", "test_ns/VersionedEnv-v3", entry_point="a:b")
        register("aec", "test_ns/VersionedEnv-v2", entry_point="a:b")

    def teardown_method(self):
        for v in (1, 2, 3):
            aec_registry.pop(f"test_ns/VersionedEnv-v{v}", None)

    def test_resolves_to_highest(self):
        s = find_spec(aec_registry, "test_ns/VersionedEnv")
        assert s.version == 3

    def test_explicit_version(self):
        s = find_spec(aec_registry, "test_ns/VersionedEnv-v1")
        assert s.version == 1


class TestErrors:
    def test_name_not_found(self):
        with pytest.raises(NameNotFound):
            find_spec(aec_registry, "classic/NonexistentEnv-v0")

    def test_namespace_not_found(self):
        with pytest.raises(NamespaceNotFound):
            find_spec(aec_registry, "bogus_ns_xyz/SomeEnv-v1")

    def test_version_not_found(self):
        register("aec", "test_ns/VerErr-v1", entry_point="a:b")
        with pytest.raises(VersionNotFound):
            find_spec(aec_registry, "test_ns/VerErr-v99")
        del aec_registry["test_ns/VerErr-v1"]


class TestSpec:
    def test_spec_lookup(self):
        register("parallel", "test_ns/SpecTest-v0", entry_point="a:b")
        s = spec("parallel", "test_ns/SpecTest-v0")
        assert s.id == "test_ns/SpecTest-v0"
        del parallel_registry["test_ns/SpecTest-v0"]


class TestMake:
    def test_make_with_callable(self):
        class FakeAEC(AECEnv):
            metadata = {"name": "fake"}

            def __init__(self, x=1):
                self.x = x

            def step(self, action):
                pass

            def reset(self, seed=None, options=None):
                pass

            def observe(self, agent):
                pass

            def render(self):
                pass

            def close(self):
                pass

        register("aec", "test_ns/FakeAEC-v0", entry_point=FakeAEC, kwargs={"x": 42})
        env = make("aec", "test_ns/FakeAEC-v0")
        assert isinstance(env, AECEnv)
        assert env.x == 42
        del aec_registry["test_ns/FakeAEC-v0"]

    def test_make_kwargs_override(self):
        class FakeParallel(ParallelEnv):
            metadata = {"name": "fake"}

            def __init__(self, y=0):
                self.y = y

            def step(self, actions):
                pass

            def reset(self, seed=None, options=None):
                pass

            def render(self):
                pass

            def close(self):
                pass

        register(
            "parallel", "test_ns/FakePar-v0", entry_point=FakeParallel, kwargs={"y": 10}
        )
        env = make("parallel", "test_ns/FakePar-v0", y=99)
        assert isinstance(env, ParallelEnv)
        assert env.y == 99
        del parallel_registry["test_ns/FakePar-v0"]
