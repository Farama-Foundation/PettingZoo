from __future__ import annotations

from unittest.mock import patch

import pytest

from pettingzoo import AECEnv
from pettingzoo.classic import rps_v2, tictactoe_v3
from pettingzoo.utils.conversions import turn_based_aec_to_parallel


class EmptyAECEnv(AECEnv):
    metadata = {"name": "empty_test_env"}
    render_mode = None

    def reset(self, seed=None, options=None):
        self.agents = []
        self.infos = {}

    def step(self, action):
        raise AssertionError("An empty environment must not be stepped")


def test_turn_based_step_with_no_initial_agents():
    env = turn_based_aec_to_parallel(EmptyAECEnv())
    assert env.reset() == ({}, {})

    for _ in range(2):
        observations, rewards, terminations, truncations, infos = env.step({})
        assert (observations, rewards, terminations, truncations, infos) == (
            {},
            {},
            {},
            {},
            {},
        )
        assert env.agents == []


@pytest.mark.parametrize(
    ("env_fn", "kwargs", "actions", "final_rewards", "terminated"),
    [
        (tictactoe_v3.env, {}, [0, 3, 1, 4, 2], [1, -1], True),
        (rps_v2.env, {"max_cycles": 1}, [0, 1], [-1, 1], False),
    ],
    ids=["termination", "truncation"],
)
def test_turn_based_step_after_dead_agents(
    env_fn, kwargs, actions, final_rewards, terminated
):
    aec_env = env_fn(**kwargs)
    env = turn_based_aec_to_parallel(aec_env)
    try:
        env.reset(seed=42)
        agents = env.agents[:]
        with patch.object(aec_env, "step", wraps=aec_env.step) as step:
            for index, action in enumerate(actions):
                observations, rewards, terminations, truncations, infos = env.step(
                    {aec_env.agent_selection: action}
                )
                for result in (observations, rewards, terminations, truncations, infos):
                    assert set(result) == set(agents)
                if index < len(actions) - 1:
                    assert not any(terminations.values())
                    assert not any(truncations.values())
                    assert env.agents == agents
                    assert all(
                        info["active_agent"] == aec_env.agent_selection
                        for info in infos.values()
                    )

            assert rewards == dict(zip(agents, final_rewards))
            assert terminations == dict.fromkeys(agents, terminated)
            assert truncations == dict.fromkeys(agents, not terminated)
            assert env.agents == aec_env.agents == []
            assert [call.args[0] for call in step.call_args_list] == actions + [
                None,
                None,
            ]

            step.reset_mock()
            for _ in range(2):
                observations, rewards, terminations, truncations, infos = env.step({})
                assert (observations, rewards, terminations, truncations, infos) == (
                    {},
                    {},
                    {},
                    {},
                    {},
                )
                assert env.agents == aec_env.agents == []
            step.assert_not_called()
    finally:
        env.close()
