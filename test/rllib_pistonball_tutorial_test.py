from __future__ import annotations

import runpy
import sys
import types
from pathlib import Path
from unittest.mock import patch


def test_rllib_pistonball_configures_registered_custom_model():
    registered_models: dict[str, type] = {}
    training_kwargs: dict[str, object] = {}
    tune_runs: list[dict[str, object]] = []

    class FakeModelCatalog:
        @staticmethod
        def register_custom_model(name: str, model_cls: type) -> None:
            registered_models[name] = model_cls

    class FakePPOConfig:
        def environment(self, **kwargs):
            return self

        def rollouts(self, **kwargs):
            return self

        def training(self, **kwargs):
            training_kwargs.update(kwargs)
            return self

        def debugging(self, **kwargs):
            return self

        def framework(self, **kwargs):
            return self

        def resources(self, **kwargs):
            return self

        def to_dict(self) -> dict[str, object]:
            return dict(training_kwargs)

    class FakeTorchModelV2:
        pass

    class FakeNNModule:
        pass

    def _make_module(name: str, **attrs) -> types.ModuleType:
        mod = types.ModuleType(name)
        for key, value in attrs.items():
            setattr(mod, key, value)
        return mod

    fake_tune = _make_module(
        "ray.tune",
        run=lambda *args, **kwargs: tune_runs.append(kwargs),
    )
    fake_registry = _make_module(
        "ray.tune.registry",
        register_env=lambda name, creator: None,
    )
    fake_ppo = _make_module("ray.rllib.algorithms.ppo", PPOConfig=FakePPOConfig)
    fake_algorithms = _make_module("ray.rllib.algorithms", ppo=fake_ppo)
    fake_pz_env = _make_module(
        "ray.rllib.env.wrappers.pettingzoo_env",
        ParallelPettingZooEnv=object,
    )
    fake_wrappers = _make_module(
        "ray.rllib.env.wrappers",
        pettingzoo_env=fake_pz_env,
    )
    fake_rllib_env = _make_module("ray.rllib.env", wrappers=fake_wrappers)
    fake_torch_modelv2 = _make_module(
        "ray.rllib.models.torch.torch_modelv2",
        TorchModelV2=FakeTorchModelV2,
    )
    fake_models_torch = _make_module(
        "ray.rllib.models.torch",
        torch_modelv2=fake_torch_modelv2,
    )
    fake_models = _make_module(
        "ray.rllib.models",
        ModelCatalog=FakeModelCatalog,
        torch=fake_models_torch,
    )
    fake_rllib = _make_module(
        "ray.rllib",
        algorithms=fake_algorithms,
        env=fake_rllib_env,
        models=fake_models,
    )
    fake_ray = _make_module(
        "ray",
        init=lambda *args, **kwargs: None,
        tune=fake_tune,
        rllib=fake_rllib,
    )
    fake_nn = _make_module("torch.nn", Module=FakeNNModule)
    fake_torch = _make_module("torch", nn=fake_nn)
    fake_supersuit = _make_module("supersuit")
    fake_pettingzoo = _make_module("pettingzoo", make=lambda *args, **kwargs: None)

    fake_modules = {
        "ray": fake_ray,
        "ray.tune": fake_tune,
        "ray.tune.registry": fake_registry,
        "ray.rllib": fake_rllib,
        "ray.rllib.algorithms": fake_algorithms,
        "ray.rllib.algorithms.ppo": fake_ppo,
        "ray.rllib.env": fake_rllib_env,
        "ray.rllib.env.wrappers": fake_wrappers,
        "ray.rllib.env.wrappers.pettingzoo_env": fake_pz_env,
        "ray.rllib.models": fake_models,
        "ray.rllib.models.torch": fake_models_torch,
        "ray.rllib.models.torch.torch_modelv2": fake_torch_modelv2,
        "torch": fake_torch,
        "torch.nn": fake_nn,
        "supersuit": fake_supersuit,
        "pettingzoo": fake_pettingzoo,
    }

    tutorial_path = (
        Path(__file__).resolve().parent.parent
        / "tutorials"
        / "Ray"
        / "rllib_pistonball.py"
    )
    with patch.dict(sys.modules, fake_modules):
        runpy.run_path(str(tutorial_path), run_name="__main__")

    assert "CNNModelV2" in registered_models
    assert training_kwargs.get("model") == {"custom_model": "CNNModelV2"}
    assert len(tune_runs) == 1
    assert tune_runs[0]["config"]["model"] == {"custom_model": "CNNModelV2"}
