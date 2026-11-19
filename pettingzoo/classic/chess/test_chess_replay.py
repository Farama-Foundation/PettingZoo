import json
import subprocess
import sys

import numpy as np

from pettingzoo.classic.chess.chess import raw_env

REPLAY_WITHOUT_OBSERVE = """
import json, sys
from pettingzoo.classic.chess.chess import raw_env

env = raw_env()
env.reset()
for action in json.loads(sys.argv[1]):
    env.step(action)
print(env.board.fen())
"""


def test_step_without_observe():
    """Recorded actions can be replayed without calling observe() first."""
    env = raw_env()
    env.reset()
    rng = np.random.default_rng(0)
    actions = []
    while not any(env.terminations.values()) and len(actions) < 100:
        action_mask = env.observe(env.agent_selection)["action_mask"]
        actions.append(int(rng.choice(np.flatnonzero(action_mask))))
        env.step(actions[-1])

    # A fresh interpreter, so that no earlier call in this process has filled
    # the move tables in chess_utils.
    replay = subprocess.run(
        [sys.executable, "-c", REPLAY_WITHOUT_OBSERVE, json.dumps(actions)],
        capture_output=True,
        text=True,
    )
    assert replay.returncode == 0, replay.stderr
    assert replay.stdout.strip() == env.board.fen()
