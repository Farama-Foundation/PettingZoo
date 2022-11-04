# noqa
"""
# Gin Rummy

```{figure} classic_gin_rummy.gif
:width: 140px
:name: gin_rummy
```

This environment is part of the <a href='..'>classic environments</a>. Please read that page first for general information.

| Import             | `from pettingzoo.classic import gin_rummy_v4` |
|--------------------|-----------------------------------------------|
| Actions            | Discrete                                      |
| Parallel API       | Yes                                           |
| Manual Control     | No                                            |
| Agents             | `agents= ['player_0', 'player_1']`            |
| Agents             | 2                                             |
| Action Shape       | Discrete(110)                                 |
| Action Values      | Discrete(110)                                 |
| Observation Shape  | (5, 52)                                       |
| Observation Values | [0,1]                                         |


Gin Rummy is a 2-player card game with a 52 card deck. The objective is to combine 3 or more cards of the same rank or in a sequence of the same suit.

Our implementation wraps [RLCard](http://rlcard.org/games.html#gin-rummy) and you can refer to its documentation for additional details. Please cite their work if you use this game in research.

### Arguments

Gin Rummy takes two optional arguments that define the reward received by a player who knocks or goes gin. The default values for the knock reward and gin reward are 0.5 and 1.0, respectively.

``` python
gin_rummy_v4.env(knock_reward = 0.5, gin_reward = 1.0, opponents_hand_visible = False)
```

`knock_reward`:  reward received by a player who knocks

`gin_reward`:  reward received by a player who goes gin

`opponents_hand_visible`:  Set to `True` to observe the entire observation space as described in `Observation Space` below. Setting it to `False` will remove any observation of the unknown cards and the observation space will only include planes 0 to 3.

### Observation Space

The observation is a dictionary which contains an `'observation'` element which is the usual RL observation described below, and an  `'action_mask'` which holds the legal moves, described in the Legal Actions Mask section.

The main observation space is 5x52 with the rows representing different planes and columns representing the 52 cards in a deck. The cards are ordered by suit (spades, hearts, diamonds, then clubs) and within each suit are ordered by rank (from Ace to King).

| Row Index | Description                                    |
|:---------:|------------------------------------------------|
|     0     | Current player's hand                          |
|     1     | Top card of the discard pile                   |
|     2     | Cards in discard pile (excluding the top card) |
|     3     | Opponent's known cards                         |
|     4     | Unknown cards                                  |

| Column Index | Description                                       |
|:------------:|---------------------------------------------------|
|    0 - 12    | Spades<br>_`0`: Ace, `1`: 2, ..., `12`: King_     |
|    13 - 25   | Hearts<br>_`13`: Ace, `14`: 2, ..., `25`: King_   |
|    26 - 38   | Diamonds<br>_`26`: Ace, `27`: 2, ..., `38`: King_ |
|    39 - 51   | Clubs<br>_`39`: Ace, `40`: 2, ..., `51`: King_    |

#### Legal Actions Mask

The legal moves available to the current agent are found in the `action_mask` element of the dictionary observation. The `action_mask` is a binary vector where each index of the vector represents whether the action is legal or not. The `action_mask` will be all zeros for any agent except the one
whose turn it is. Taking an illegal move ends the game with a reward of -1 for the illegally moving agent and a reward of 0 for all other agents.

### Action Space

There are 110 actions in Gin Rummy.

| Action ID | Action                                                                                                                                                                                 |
|:---------:|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|     0     | Score Player 0<br>_Used after knock, gin, or dead hand to compute the player's hand._                                                                                                  |
|     1     | Score Player 1<br>_Used after knock, gin, or dead hand to compute the player's hand._                                                                                                  |
|     2     | Draw a card                                                                                                                                                                            |
|     3     | Pick top card from Discard pile                                                                                                                                                        |
|     4     | Declare dead hand                                                                                                                                                                      |
|     5     | Gin                                                                                                                                                                                    |
|   6 - 57  | Discard a card<br>_`6`: A-Spades, `7`: 2-Spades, ..., `18`: K-Spades<br>`19`: A-Hearts ... `31`: K-Hearts<br>`32`: A-Diamonds ... `44`: K-Diamonds<br>`45`: A-Clubs ... `57`: K-Clubs_ |
|  58 - 109 | Knock<br>_`58`: A-Spades, `59`: 2-Spades, ..., `70`: K-Spades<br>`71`: A-Hearts ... `83`: K-Hearts<br>`84`: A-Diamonds ... `96`: K-Diamonds<br>`97`: A-Clubs ... `109`: K-Clubs_       |

For example, you would use action `2` to draw a card or action `3` to pick up a discarded card.

### Rewards

At the end of the game, a player who gins is awarded 1 point, a player who knocks is awarded 0.5 points, and the losing player receives a reward equal to the negative of their deadwood count.

If the hand is declared dead, both players get a reward equal to negative of their deadwood count.

| End Action                                | Winner | Loser                   |
| ----------------------------------------- | :----: | ----------------------- |
| Dead Hand<br>_Both players are penalized_ |   --   | `-deadwood_count / 100` |
| Knock<br>_Knocking player: Default +0.5_  |   --   | `-deadwood_count / 100` |
| Gin<br>_Going Gin Player: Default +1_     |   --   | `-deadwood_count / 100` |

Note that the defaults are slightly different from those in RLcard- their default reward for knocking is 0.2.

Penalties of `deadwood_count / 100` ensure that the reward never goes below -1.

### Version History

* v4: Upgrade to RLCard 1.0.3 (1.11.0)
* v3: Fixed bug in arbitrary calls to observe() (1.8.0)
* v2: Bumped RLCard version, bug fixes, legal action mask in observation replaced illegal move list in infos (1.5.0)
* v1: Bumped RLCard version, fixed observation space, adopted new agent iteration scheme where all agents are iterated over after they are done (1.4.0)
* v0: Initial versions release (1.0.0)

"""

import gymnasium
import numpy as np
from gymnasium.utils import EzPickle
from rlcard.games.gin_rummy.player import GinRummyPlayer
from rlcard.games.gin_rummy.utils import melding as melding
from rlcard.games.gin_rummy.utils import utils
from rlcard.games.gin_rummy.utils.action_event import GinAction, KnockAction
from rlcard.utils.utils import print_card

from pettingzoo.utils import wrappers

from .rlcard_base import RLCardBase


def env(**kwargs):
    render_mode = kwargs.get("render_mode")
    if render_mode == "ansi":
        kwargs["render_mode"] = "human"
        env = raw_env(**kwargs)
        env = wrappers.CaptureStdoutWrapper(env)
    else:
        env = raw_env(**kwargs)
    env = wrappers.TerminateIllegalWrapper(env, illegal_reward=-1)
    env = wrappers.AssertOutOfBoundsWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env


class raw_env(RLCardBase, EzPickle):

    metadata = {
        "render_modes": ["human"],
        "name": "gin_rummy_v4",
        "is_parallelizable": False,
        "render_fps": 1,
    }

    def __init__(
        self,
        knock_reward: float = 0.5,
        gin_reward: float = 1.0,
        opponents_hand_visible=False,
        render_mode=None,
    ):
        EzPickle.__init__(self, knock_reward, gin_reward, render_mode)
        self._opponents_hand_visible = opponents_hand_visible
        num_planes = 5 if self._opponents_hand_visible else 4
        RLCardBase.__init__(self, "gin-rummy", 2, (num_planes, 52))
        self._knock_reward = knock_reward
        self._gin_reward = gin_reward

        self.env.game.judge.scorer.get_payoff = self._get_payoff
        self.render_mode = render_mode

    def _get_payoff(self, player: GinRummyPlayer, game) -> float:
        going_out_action = game.round.going_out_action
        going_out_player_id = game.round.going_out_player_id
        if (
            going_out_player_id == player.player_id
            and type(going_out_action) is KnockAction
        ):
            payoff = self._knock_reward
        elif (
            going_out_player_id == player.player_id
            and type(going_out_action) is GinAction
        ):
            payoff = self._gin_reward
        else:
            hand = player.hand
            best_meld_clusters = melding.get_best_meld_clusters(hand=hand)
            best_meld_cluster = [] if not best_meld_clusters else best_meld_clusters[0]
            deadwood_count = utils.get_deadwood_count(hand, best_meld_cluster)
            payoff = -deadwood_count / 100
        return payoff

    def observe(self, agent):
        obs = self.env.get_state(self._name_to_int(agent))
        if self._opponents_hand_visible:
            observation = obs["obs"].astype(self._dtype)
        else:
            observation = obs["obs"][0:4, :].astype(self._dtype)

        legal_moves = self.next_legal_moves
        action_mask = np.zeros(110, "int8")
        for i in legal_moves:
            action_mask[i] = 1

        return {"observation": observation, "action_mask": action_mask}

    def render(self):
        if self.render_mode is None:
            gymnasium.logger.warn(
                "You are calling render method without specifying any render mode."
            )
            return

        for player in self.possible_agents:
            state = self.env.game.round.players[self._name_to_int(player)].hand
            print(f"\n===== {player}'s Hand =====")
            print_card([c.__str__()[::-1] for c in state])
        state = self.env.game.get_state(0)
        print("\n==== Top Discarded Card ====")
        print_card([c.__str__() for c in state["top_discard"]] if state else None)
        print("\n")
