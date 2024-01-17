from pettingzoo.mpe import (
    simple_adversary_v3,
    simple_crypto_v3,
    simple_push_v3,
    simple_reference_v3,
    simple_speaker_listener_v4,
    simple_spread_v3,
    simple_tag_v3,
    simple_v3,
    simple_world_comm_v3,
)
from pettingzoo.utils.deprecated_module import deprecated_handler

mpe_environments = {
    "mpe/simple_adversary_v3": simple_adversary_v3,
    "mpe/simple_crypto_v3": simple_crypto_v3,
    "mpe/simple_push_v3": simple_push_v3,
    "mpe/simple_reference_v3": simple_reference_v3,
    "mpe/simple_speaker_listener_v4": simple_speaker_listener_v4,
    "mpe/simple_spread_v3": simple_spread_v3,
    "mpe/simple_tag_v3": simple_tag_v3,
    "mpe/simple_world_comm_v3": simple_world_comm_v3,
    "mpe/simple_v3": simple_v3,
}


def __getattr__(env_name):
    return deprecated_handler(env_name, __path__, __name__)
