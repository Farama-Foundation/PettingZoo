from ray import tune
from ray.rllib.models import ModelCatalog
from ray.tune.registry import register_env
from ray.rllib.utils import try_import_tf
from ray.rllib.env.pettingzoo_env import ParallelPettingZooEnv
from pettingzoo.butterfly import pistonball_v3
import supersuit as ss

# for APEX-DQN
from ray.rllib.models.tf.tf_modelv2 import TFModelV2

tf1, tf, tfv = try_import_tf()


class MLPModelV2(TFModelV2):
    def __init__(self, obs_space, action_space, num_outputs, model_config,
                 name="my_model"):
        super(MLPModelV2, self).__init__(obs_space, action_space, num_outputs, model_config, name)
        input_layer = tf.keras.layers.Input(obs_space.shape, dtype=obs_space.dtype)
        conv_1 = tf.keras.layers.Conv2D(32, kernel_size=(8, 8), strides=4, activation="relu")(input_layer)
        conv_2 = tf.keras.layers.Conv2D(64, kernel_size=(4, 4), strides=2, activation="relu")(conv_1)
        conv_3 = tf.keras.layers.Conv2D(64, kernel_size=(3, 3), strides=1, activation="relu")(conv_2)
        flatten = tf.keras.layers.Flatten()(conv_3)
        dense_1 = tf.keras.layers.Dense(512, activation="relu")(flatten)

        output = tf.keras.layers.Dense(num_outputs, activation=None)(dense_1)
        value_out = tf.keras.layers.Dense(1, activation=None, name="value_out")(dense_1)
        self.base_model = tf.keras.Model(input_layer, [output, value_out])
        self.register_variables(self.base_model.variables)

    def forward(self, input_dict, state, seq_lens):
        model_out, self._value_out = self.base_model(input_dict["obs"])
        return model_out, state

    def value_function(self):
        return tf.reshape(self._value_out, [-1])


def make_env_creator():
    def env_creator(args):
        env = pistonball_v3.parallel_env(n_pistons=20, local_ratio=0, time_penalty=-0.1, continuous=True, random_drop=True, random_rotate=True, ball_mass=0.75, ball_friction=0.3, ball_elasticity=1.5, max_cycles=125)
        env = ss.color_reduction_v0(env, mode='B')
        env = ss.dtype_v0(env, 'float32')
        env = ss.resize_v0(env, x_size=84, y_size=84)
        env = ss.normalize_obs_v0(env, env_min=0, env_max=1)
        env = ss.frame_stack_v1(env, 3)
        #env = ss.flatten_v0(env)
        return env
    return env_creator


if __name__ == "__main__":

    env_creator = make_env_creator()

    env_name = "pistonball_v3"

    register_env(env_name, lambda config: ParallelPettingZooEnv(env_creator(config)))

    test_env = ParallelPettingZooEnv(env_creator({}))
    obs_space = test_env.observation_space
    act_space = test_env.action_space

    ModelCatalog.register_custom_model("MLPModelV2", MLPModelV2)

    def gen_policy(i):
        config = {
            "model": {
                "custom_model": "MLPModelV2",
            },
            "gamma": 0.99,
        }
        return (None, obs_space, act_space, config)

    policies = {"policy_0": gen_policy(0)}

    policy_ids = list(policies.keys())

    tune.run(
        "PPO",
        name="PPO",
        stop={"episodes_total": 20000},
        checkpoint_freq=50,
        local_dir="~/ray_results/"+env_name,
        config={
            # Environment specific
            "env": env_name,
            # General
            "log_level": "ERROR",
            "num_gpus": 1,
            "num_workers": 4,
            "num_envs_per_worker": 4,
            "compress_observations": False,
            "batch_mode": 'truncate_episodes',

            'use_critic': True,
            'use_gae': True,
            "lambda": 0.95,

            "gamma": .99,
            'horizon': None,
            'soft_horizon': False,  

            "kl_coeff": 0.5,
            "clip_rewards": True,  
            "clip_param": 0.1,
            "vf_clip_param": 10.0,
            'grad_clip': None,
            "entropy_coeff": 0.001,
            "train_batch_size": 5000,
            'vf_loss_coeff': 1.0,

            "sgd_minibatch_size": 500,
            "num_sgd_iter": 10,
            'rollout_fragment_length': 200,  
            'lr': 5e-05,
            'clip_actions': True,

            # Method specific
            "multiagent": {
                "policies": policies,
                "policy_mapping_fn": (
                    lambda agent_id: policy_ids[0]),
            },
        },
    )
