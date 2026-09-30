import io
from contextlib import redirect_stdout

from pettingzoo.classic import connect_four_v3
from pettingzoo.utils.average_total_reward import average_total_reward
from pettingzoo.utils.env_logger import EnvLogger


def test_average_total_reward_does_not_sample_illegal_moves():
    EnvLogger.flush()
    env = connect_four_v3.env()
    with redirect_stdout(io.StringIO()):
        result = average_total_reward(env, max_episodes=20, max_steps=100000)
    assert isinstance(result, float)
    assert not any("Illegal move" in str(msg) for msg in EnvLogger.mqueue)
