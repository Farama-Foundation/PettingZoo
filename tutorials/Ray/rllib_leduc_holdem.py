"""Uses Ray's RLLib to train agents to play Leduc Holdem.

Author: Rohan (https://github.com/Rohan138)
"""

import os

from gymnasium.spaces import Box
from ray import tune
from ray.rllib.algorithms.dqn import DQNConfig
from ray.rllib.algorithms.dqn.dqn_torch_model import DQNTorchModel
from ray.rllib.env import PettingZooEnv
from ray.rllib.models import ModelCatalog
from ray.rllib.models.torch.fcnet import FullyConnectedNetwork as TorchFC
from ray.rllib.utils.framework import try_import_torch
from ray.rllib.utils.torch_utils import FLOAT_MAX
from ray.tune.registry import register_env

from pettingzoo.classic import leduc_holdem_v4

raise NotImplementedError(
    "There are currently bugs in this tutorial, we will fix them soon."
)

torch, nn = try_import_torch()


class TorchMaskedActions(DQNTorchModel):
    """PyTorch version of above ParametricActionsModel."""

    def __init__(self, obs_space, action_space, num_outputs, model_config, name, **kw):
        DQNTorchModel.__init__(
            self, obs_space, action_space, num_outputs, model_config, name, **kw
        )

        obs_len = obs_space.shape[0] - action_space.n

        orig_obs_space = Box(
            shape=(obs_len,), low=obs_space.low[:obs_len], high=obs_space.high[:obs_len]
        )
        self.action_embed_model = TorchFC(
            orig_obs_space,
            action_space,
            action_space.n,
            model_config,
            name + "_action_embed",
        )

    def forward(self, input_dict, state, seq_lens):
        # Extract the available actions tensor from the observation.
        action_mask = input_dict["obs"]["action_mask"]

        # Compute the predicted action embedding
        action_logits, _ = self.action_embed_model(
            {"obs": input_dict["obs"]["observation"]}
        )
        # turns probit action mask into logit action mask
        inf_mask = torch.clamp(torch.log(action_mask), -1e10, FLOAT_MAX)

        return action_logits + inf_mask, state

    def value_function(self):
        return self.action_embed_model.value_function()


if __name__ == "__main__":
    alg_name = "DQN"
    ModelCatalog.register_custom_model("pa_model", TorchMaskedActions)
    # function that outputs the environment you wish to register.

    def env_creator():
        env = leduc_holdem_v4.env()
        return env

    register_env("leduc_holdem", lambda config: PettingZooEnv(env_creator()))

    test_env = PettingZooEnv(env_creator())
    obs_space = test_env.observation_space
    print(obs_space)
    act_space = test_env.action_space

    config = (
        DQNConfig()
        .environment(env="leduc_holdem")
        .rollouts(num_rollout_workers=1, rollout_fragment_length=30, horizon=200)
        .training(
            train_batch_size=200,
            hiddens=[],
            dueling=False,
            model={"custom_model": "pa_model"},
        )
        .multi_agent(
            policies={
                "player_0": (None, obs_space, act_space, {}),
                "player_1": (None, obs_space, act_space, {}),
            },
            policy_mapping_fn=lambda agent_id: agent_id,
        )
        .resources(num_gpus=int(os.environ.get("RLLIB_NUM_GPUS", "0")))
        .debugging(log_level="DEBUG")
        .framework(framework="torch")
        .exploration(
            exploration_config={
                # The Exploration class to use.
                "type": "EpsilonGreedy",
                # Config for the Exploration class' constructor:
                "initial_epsilon": 0.1,
                "final_epsilon": 0.0,
                "epsilon_timesteps": 100000,  # Timesteps over which to anneal epsilon.
            }
        )
    )

    tune.run(
        alg_name,
        name="DQN",
        stop={"timesteps_total": 10000000},
        checkpoint_freq=10,
        config=config.to_dict(),
    )
