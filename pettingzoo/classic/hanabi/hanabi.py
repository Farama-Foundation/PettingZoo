# noqa: D212, D415
"""
# Hanabi

```{figure} classic_hanabi.gif
:width: 140px
:name: hanabi
```

This environment is part of the <a href='..'>classic environments</a>. Please read that page first for general information.

| Import               | `from pettingzoo.classic import hanabi_v5` |
|----------------------|--------------------------------------------|
| Actions              | Discrete                                   |
| Parallel API         | Yes                                        |
| Manual Control       | No                                         |
| Agents               | `agents= ['player_0', 'player_1']`         |
| Agents               | 2                                          |
| Action Shape         | Discrete(20)                               |
| Action Values        | Discrete(20)                               |
| Observation Shape    | (658,)                                     |
| Observation Values   | [0,1]                                      |


Hanabi is a 2-5 player cooperative game where players work together to form fireworks of different colors. A firework is a set of cards of the same color, ordered from 1 to 5. Cards in the game have both a color and number; each player can view the cards another player holds, but not their own.
Players cannot directly communicate with each other, but must instead remove an info token from play in order to give information. Players can tell other players which of the cards in their hand is a specific color, or a specific number. There are initially 8 info tokens, but players can discard
cards in their hand to return an info token into play. Players can also play a card from their hand: the card must either begin a new firework or be appended in order to an existing firework. However, 2 fireworks cannot have the same color, and a single firework cannot repeat numbers. If the
played card does not satisfy these conditions, a life token is placed. The game ends when either 3 life tokens have been placed, all 5 fireworks have been completed, or all cards have been drawn from the deck. Points are awarded based on the largest card value in each created firework.

### Environment arguments

Hanabi takes in a number of arguments defining the size and complexity of the game. Default is a full 2 player hanabi game.

``` python
hanabi_v5.env(colors=5, ranks=5, players=2, hand_size=5, max_information_tokens=8,
max_life_tokens=3, observation_type='minimal')
```

`colors`: Number of colors the cards can take (affects size of deck)

`ranks`: Number of ranks the cards can take (affects size of deck)

`hand_size`: Size of player's hands. Standard game is (4 if players >= 4 else 5)

`max_information_tokens`: Maximum number of information tokens (more tokens makes the game easier by allowing more information to be revealed)

`max_life_tokens`: Maximum number of life tokens (more tokens makes the game easier by allowing more information to be revealed)

`observation_type`:
    "minimal": Minimal observation (what a human sees).
    "card_knowledge": includes per-card knowledge of past hints, as well as simple inferred knowledge of the form
        "this card is not red, because it was not revealed as red in a past".
    "seer" shows all cards, including the player's own cards, regardless of what hints have been given.

### Observation Space

The observation is a dictionary which contains an `'observation'` element which is the usual RL observation described below, and an  `'action_mask'` which holds the legal moves, described in the Legal Actions Mask section.

The main observation space of an agent is a 658 sized vector representing the life and info tokens left, the currently constructed fireworks, the hands of all other agents, the current deck size and the discarded cards. The observation vector contains the following features, life tokens,
information tokens, number of players, deck size, formed fireworks, legal moves, observed hands, discard pile, the hints received from other players, which are then serialized into a bit string.

Each card is encoded with a 25 bit one-hot vector, where the encoding of a card is equal to its color*T + rank, where T is the max possible rank. By default this value is 5. The maximum deck size is 50. The remaining deck size is represented with unary encoding. The state of each colored
firework is represented with a one-hot encoding. The information tokens remaining are represented with a unary encoding. The life tokens remaining are represented with a unary encoding. The discard pile is represented with a thermometer encoding of the ranks of each discarded card. That is the
least significant bit being set to 1 indicates the lowest rank card of that color has been discarded.

As players reveal info about their cards, the information revealed per card is also observed. The first 25 bits represent whether or not that specific card could be a specific color. For example if the card could only be red, then the first 25 bits of the observed revealed info would be 11111
followed by 20 zeros. The next 5 bits store whether the color of that card was explicitly revealed, so if the card was revealed to be red, then the next 5 bits would be 10000. Finally the last 5 bits are the revealed rank of the card. So if the card was revealed to be of rank 1, then the next 5
bits would be 10000. These 25 bits are tracked and observed for all cards in each player's hand.

|  Index  | Description                                     |  Values  |
|:-------:|-------------------------------------------------|:--------:|
|  0 - 24 | Vector of Card 1 in other player's hand         |  [0, 1]  |
| 25 - 49 | Vector of Card 2 in other player's hand         |  [0, 1]  |
| 50 - 74 | Vector of Card 3 in other player's hand         |  [0, 1]  |
| 75 -100 | Vector of Card 4 in other player's hand         |  [0, 1]  |
| 100-124 | Vector of Card 5 in other player's hand         |  [0, 1]  |
| 125-174 | Unary Encoding of Remaining Deck Size           |  [0, 1]  |
| 175-179 | Vector of Red Firework                          |  [0, 1]  |
| 180-184 | Vector of Yellow Firework                       |  [0, 1]  |
| 185-189 | Vector of Green Firework                        |  [0, 1]  |
| 190-195 | Vector of White Firework                        |  [0, 1]  |
| 195-199 | Vector of Blue Firework                         |  [0, 1]  |
| 200-207 | Unary Encoding of Remaining Info Tokens         |  [0, 1]  |
| 208-210 | Unary Encoding of Remaining Life Tokens         |  [0, 1]  |
| 211-260 | Thermometer Encoding of Discard Pile            |  [0, 1]  |
| 261-262 | One-Hot Encoding of Previous Player ID          |  [0, 1]  |
| 263-266 | Vector of Previous Player's Action Type         |  [0, 1]  |
| 267-268 | Vector of Target from Previous Action           |  [0, 1]  |
| 269-273 | Vector of the Color Revealed in Last Action     |  [0, 1]  |
| 274-278 | Vector of the Rank Revealed in Last Action      |  [0, 1]  |
| 279-280 | Vector of Which Cards in the Hand were Revealed |  [0, 1]  |
| 281-282 | Position of the Card that was played or dropped |  [0, 1]  |
| 283-307 | Vector Representing Card that was last played   |  [0, 1]  |
| 308-342 | Revealed Info of This Player's 0th Card         |  [0, 1]  |
| 343-377 | Revealed Info of This Player's 1st Card         |  [0, 1]  |
| 378-412 | Revealed Info of This Player's 2nd Card         |  [0, 1]  |
| 413-447 | Revealed Info of This Player's 3rd Card         |  [0, 1]  |
| 445-482 | Revealed Info of This Player's 4th Card         |  [0, 1]  |
| 483-517 | Revealed Info of Other Player's 0th Card        |  [0, 1]  |
| 518-552 | Revealed Info of Other Player's 1st Card        |  [0, 1]  |
| 553-587 | Revealed Info of Other Player's 2nd Card        |  [0, 1]  |
| 588-622 | Revealed Info of Other Player's 3rd Card        |  [0, 1]  |
| 663-657 | Revealed Info of Other Player's 4th Card        |  [0, 1]  |


#### Legal Actions Mask

The legal moves available to the current agent are found in the `action_mask` element of the dictionary observation. The `action_mask` is a binary vector where each index of the vector represents whether the action is legal or not. The `action_mask` will be all zeros for any agent except the one
whose turn it is. Taking an illegal move ends the game with a reward of -1 for the illegally moving agent and a reward of 0 for all other agents.

### Action Space

The action space is a scalar value, which ranges from 0 to the max number of actions. The values represent all possible actions a player can make, legal or not. Each possible move in the environment is mapped to a UUID, which ranges from 0 to the max number of moves. By default the max number of
moves is 20. The first range of actions are to discard a card in the agent's hand. If there are k cards in the player's hand, then the first k action values are to discard one of those cards. The next k actions would be to play one of the cards in the player's hand. Finally, the remaining actions
are to reveal a color or rank in another players hand. The first set of reveal actions would be revealing all colors or values of cards for the next player in order, and this repeats for all the other players in the environment.

| Action ID | Action                                                      |
|:---------:|-------------------------------------------------------------|
|     0     | Discard Card at position 0                                  |
|     1     | Discard Card at position 1                                  |
|     2     | Discard Card at position 2                                  |
|     3     | Discard Card at position 3                                  |
|     4     | Discard Card at position 4                                  |
|     5     | Play Card at position 0                                     |
|     6     | Play Card at position 1                                     |
|     7     | Play Card at position 2                                     |
|     8     | Play Card at position 3                                     |
|     9     | Play Card at position 4                                     |
|    10     | Reveal Red Cards for Player 1                               |
|    11     | Reveal Yellow Cards for Player 1                            |
|    12     | Reveal Green Cards for Player 1                             |
|    13     | Reveal White Cards for Player 1                             |
|    14     | Reveal Blue Cards for Player 1                              |
|    15     | Reveal Rank 1 Cards for Player 1                            |
|    16     | Reveal Rank 2 Cards for Player 1                            |
|    17     | Reveal Rank 3 Cards for Player 1                            |
|    18     | Reveal Rank 4 Cards for Player 1                            |
|    19     | Reveal Rank 5 Cards for Player 1                            |

### Rewards

The reward of each step is calculated as the change in game score from the last step. The game score is calculated as the sum of values in each constructed firework. If the game is lost, the score is set to zero, so the final reward will be the negation of all reward received so far.

For example, if fireworks were created as follows:

Blue 1, Blue 2, Red 1, Green 1, Green 2, Green 3

At the end of the game, the total score would be 2 + 1 + 3 = 6

If an illegal action is taken, the game terminates and the one player that took the illegal action loses. Like an ordinary loss, their final reward will be the negation of all reward received so far. The reward of the other players will not be affected by the illegal action.


### Version History

* v5: Switched environment to depend on OpenSpiel (using Shimmy) for future compatibility (1.23.0)
* v4: Fixed bug in arbitrary calls to observe() (1.8.0)
* v3: Legal action mask in observation replaced illegal move list in infos (1.5.0)
* v2: Fixed default parameters (1.4.2)
* v1: Bumped version of all environments due to adoption of new agent iteration scheme where all agents are iterated over after they are done (1.4.0)
* v0: Initial versions release (1.0.0)

"""

from typing import List, Optional, Union

import gymnasium
import numpy as np
from gymnasium import spaces
from gymnasium.utils import EzPickle
from shimmy.openspiel_compatibility import OpenSpielCompatibilityV0

from pettingzoo import AECEnv
from pettingzoo.utils import wrappers
from pettingzoo.utils.agent_selector import agent_selector


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


class raw_env(AECEnv, EzPickle):
    metadata = {
        "render_modes": ["human"],
        "name": "hanabi_v5",
        "is_parallelizable": False,
        "render_fps": 2,
    }

    # set of all required params
    required_keys: set = {
        "colors",
        "ranks",
        "players",
        "hand_size",
        "max_information_tokens",
        "max_life_tokens",
        "observation_type",
        "random_start_player",
    }

    def __init__(
        self,
        colors: int = 5,
        ranks: int = 5,
        players: int = 2,
        hand_size: int = 5,
        max_information_tokens: int = 8,
        max_life_tokens: int = 3,
        observation_type: str = "card_knowledge",
        random_start_player: bool = False,
        render_mode: Optional[str] = None,
    ):
        """Initializes the `raw_env` class.

        Parameter descriptions :
              - colors: int, Number of colors in [2,5].
              - ranks: int, Number of ranks in [2,5].
              - players: int, Number of players in [2,5].
              - hand_size: int, Hand size in [2,5].
              - max_information_tokens: int, Number of information tokens (>=0).
              - max_life_tokens: int, Number of life tokens (>=1).
              - observation_type: str.
                    "minimal"": Minimal observation.
                    "card_knowledge": First-order common knowledge observation.
                    "seer": Full information of all cards.
              - random_start_player: bool, Random start player.

        Common game configurations:
            Hanabi-Full (default) :  {
                "colors": 5,
                "ranks": 5,
                "players": 2,
                "max_information_tokens": 8,
                "max_life_tokens": 3,
                "hand_size": (4 if players >= 4 else 5)
                "observation_type": "card_knowledge",
                "hand_size": 2,
                }

            Hanabi-Small : {
                "colors": 2,
                "ranks": 5,
                "players": 2,
                "max_information_tokens": 3,
                "hand_size": 2,
                "max_life_tokens": 1,
                "observation_type": "card_knowledge",
                }

            Hanabi-Very-Small : {
                "colors": 1,
                "ranks": 5,
                "players": 2,
                "max_information_tokens": 3,
                "hand_size": 2,
                "max_life_tokens": 1,
                "observation_type": "card_knowledge",
                }

        """
        EzPickle.__init__(
            self,
            colors=colors,
            ranks=ranks,
            players=players,
            hand_size=hand_size,
            max_information_tokens=max_information_tokens,
            max_life_tokens=max_life_tokens,
            observation_type=observation_type,
            random_start_player=random_start_player,
            render_mode=render_mode,
        )

        # ToDo: Starts
        # Check if all possible dictionary values are within a certain ranges.
        self._raise_error_if_config_values_out_of_range(
            colors,
            ranks,
            players,
            hand_size,
            max_information_tokens,
            max_life_tokens,
            observation_type,
            random_start_player,
        )

        self._config = {
            "colors": colors,
            "ranks": ranks,
            "players": players,
            "hand_size": hand_size,
            "max_information_tokens": max_information_tokens,
            "max_life_tokens": max_life_tokens,
            "observation_type": observation_type,
            "random_start_player": random_start_player,
        }
        self.hanabi_env = OpenSpielCompatibilityV0(
            game_name="hanabi", render_mode=render_mode, config=self._config
        )

        # List of agent names
        self.possible_agents = self.hanabi_env.possible_agents
        self.agent_selection: str

        self.action_spaces = {
            a: self.hanabi_env.action_space(a) for a in self.possible_agents
        }
        self.observation_spaces = {
            a: spaces.Dict(
                {
                    "observation": self.hanabi_env.observation_space(a),
                    "action_mask": spaces.Box(
                        low=0,
                        high=1,
                        shape=(self.hanabi_env.action_space(a).n,),
                        dtype=np.int8,
                    ),
                }
            )
            for a in self.possible_agents
        }

        self.render_mode = render_mode

    def observation_space(self, agent):
        return self.observation_spaces[agent]

    def action_space(self, agent):
        return self.action_spaces[agent]

    @staticmethod
    def _raise_error_if_config_values_out_of_range(
        colors,
        ranks,
        players,
        hand_size,
        max_information_tokens,
        max_life_tokens,
        observation_type,
        random_start_player,
    ):
        if not (2 <= colors <= 5):
            raise ValueError(
                f"Config parameter {colors} is out of bounds. See description in hanabi.py."
            )

        elif not (2 <= ranks <= 5):
            raise ValueError(
                f"Config parameter {ranks} is out of bounds. See description in hanabi.py."
            )

        elif not (2 <= players <= 5):
            raise ValueError(
                f"Config parameter {players} is out of bounds. See description in hanabi.py."
            )

        elif not (players <= colors):
            raise ValueError(
                f"Config parameter colors: {colors} is smaller than players: {players}, which is not allowed. See description in hanabi.py."
            )

        elif not (2 <= hand_size <= 5):
            raise ValueError(
                f"Config parameter {hand_size} is out of bounds. See description in hanabi.py."
            )

        elif not (0 <= max_information_tokens):
            raise ValueError(
                f"Config parameter {max_information_tokens} is out of bounds. See description in hanabi.py."
            )

        elif not (1 <= max_life_tokens):
            raise ValueError(
                f"Config parameter {max_life_tokens} is out of bounds. See description in hanabi.py."
            )

        elif not (observation_type in ["minimal", "card_knowledge", "seer"]):
            raise ValueError(
                f"Config parameter {observation_type} must be either 'minimal', 'card_knowledge', or 'seer'. See description in hanabi.py."
            )

    @property
    def observation_vector_dim(self):
        return self.hanabi_env.observation_space(self.possible_agents[0]).shape

    @property
    def legal_moves(self) -> List[int]:
        mask = self.hanabi_env.infos[self.agent_selection]["action_mask"]
        return [i for i in range(len(mask)) if mask[i] == 1]

    @property
    def all_moves(self) -> List[int]:
        mask = self.hanabi_env.infos[self.agent_selection]["action_mask"]
        return [i for i in range(len(mask))]

    # ToDo: Fix Return value
    def reset(self, seed=None, options=None):
        """Resets the environment for a new game and returns observations of current player as List of ints.

        Returns:
            observation: Optional list of integers of length self.observation_vector_dim, describing observations of
            current agent (agent_selection).
        """
        self.agents = self.possible_agents[:]

        self.hanabi_env.reset(seed=seed)

        # Reset spaces
        self.action_spaces = {a: self.hanabi_env.action_space(a) for a in self.agents}
        self.observation_spaces = {
            a: spaces.Dict(
                {
                    "observation": self.hanabi_env.observation_space(a),
                    "action_mask": spaces.Box(
                        low=0,
                        high=1,
                        shape=(self.hanabi_env.action_space(a).n,),
                        dtype=np.int8,
                    ),
                }
            )
            for a in self.agents
        }

        self.rewards = self.hanabi_env.rewards
        self._cumulative_rewards = self.hanabi_env._cumulative_rewards
        self.agent_selection = self.hanabi_env.agent_selection
        self.rewards = self.hanabi_env.rewards
        self.terminations = self.hanabi_env.terminations
        self.truncations = self.hanabi_env.truncations
        self.infos = self.hanabi_env.infos

        self._agent_selector = agent_selector(self.agents)
        self.agent_selection = self._agent_selector.reset()

    def step(
        self, action: int, observe: bool = True, as_vector: bool = True
    ) -> Optional[Union[np.ndarray, List[List[dict]]]]:
        """Advances the environment by one step. Action must be within self.legal_moves, otherwise throws error.

        Returns:
            observation: Optional List of new observations of agent at turn after the action step is performed.
            By default, a list of integers, describing the logic state of the game from the view of the agent.
            Can be a returned as a descriptive dictionary, if as_vector=False.
        """
        if (
            self.terminations[self.agent_selection]
            or self.truncations[self.agent_selection]
        ):
            return self._was_dead_step(action)

        self.hanabi_env.step(action)

        self.agent_selection = self.hanabi_env.agent_selection
        self.rewards = self.hanabi_env.rewards
        self.terminations = self.hanabi_env.terminations
        self.truncations = self.hanabi_env.truncations
        self.infos = self.hanabi_env.infos

        if self.render_mode is not None:
            self.render()

    def observe(self, agent_name: str):
        observation = self.hanabi_env.observe(agent_name)
        mask = self.infos[agent_name]["action_mask"]
        return {"observation": observation, "action_mask": mask}

    def render(self):
        """Prints player's data.

        Supports console print only.
        """
        if self.render_mode is None:
            gymnasium.logger.warn(
                "You are calling render method without specifying any render mode."
            )
            return
        try:
            self.hanabi_env.render()
        except NotImplementedError:
            return

    def close(self):
        pass
