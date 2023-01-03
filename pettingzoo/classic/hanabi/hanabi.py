# noqa
"""
# Hanabi

```{figure} classic_hanabi.gif
:width: 140px
:name: hanabi
```

This environment is part of the <a href='..'>classic environments</a>. Please read that page first for general information.

| Import               | `from pettingzoo.classic import hanabi_v4` |
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
hanabi_v4.env(colors=5, rank=5, players=2, hand_size=5, max_information_tokens=8,
max_life_tokens=3, observation_type=1)
```

`colors`: Number of colors the cards can take (affects size of deck)

`rank`: Number of ranks the cards can take (affects size of deck)

`hand_size`: Size of player's hands. Standard game is (4 if players >= 4 else 5)

`max_information_tokens`: Maximum number of information tokens (more tokens makes the game easier by allowing more information to be revealed)

`max_life_tokens`: Maximum number of life tokens (more tokens makes the game easier by allowing more information to be revealed)

`observation_type`: 0: Minimal observation. 1: First-order common knowledge observation (default).

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

* v4: Fixed bug in arbitrary calls to observe() (1.8.0)
* v3: Legal action mask in observation replaced illegal move list in infos (1.5.0)
* v2: Fixed default parameters (1.4.2)
* v1: Bumped version of all environments due to adoption of new agent iteration scheme where all agents are iterated over after they are done (1.4.0)
* v0: Initial versions release (1.0.0)

"""

from typing import Dict, List, Optional, Union

import gymnasium
import numpy as np
from gymnasium import spaces
from gymnasium.utils import EzPickle

from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector, wrappers

# importing Hanabi and throw error message if pypi package is not installed correctly.
try:
    from hanabi_learning_environment.rl_env import HanabiEnv

except ModuleNotFoundError as e:
    raise ImportError(
        (
            "Hanabi is not installed.\n",
            "Run ´pip3 install hanabi_learning_environment´ from within your project environment.\n",
            "Consult hanabi/README.md for detailed information.",
        )
    ) from e
"""
Wrapper class around Deepmind's Hanabi Learning Environment.
"""


class HanabiScorePenalty:
    def __init__(self, env):
        self.env = env

    def __float__(self):
        return -float(self.env.hanabi_env.state.score())


def env(**kwargs):
    render_mode = kwargs.get("render_mode")
    if render_mode == "ansi":
        kwargs["render_mode"] = "human"
        env = raw_env(**kwargs)
        env = wrappers.CaptureStdoutWrapper(env)
    else:
        env = raw_env(**kwargs)

    env = wrappers.TerminateIllegalWrapper(env, illegal_reward=HanabiScorePenalty(env))
    env = wrappers.AssertOutOfBoundsWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env


class raw_env(AECEnv, EzPickle):
    """This class capsules endpoints provided within deepmind/hanabi-learning-environment/rl_env.py."""

    metadata = {
        "render_modes": ["human"],
        "name": "hanabi_v4",
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
        observation_type: int = 1,
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
              - observation_type: int.
                    0: Minimal observation.
                    1: First-order common knowledge observation.
              - random_start_player: bool, Random start player.

        Common game configurations:
            Hanabi-Full (default) :  {
                "colors": 5,
                "ranks": 5,
                "players": 2,
                "max_information_tokens": 8,
                "max_life_tokens": 3,
                "hand_size": (4 if players >= 4 else 5)
                "observation_type": 1,
                "hand_size": 2
                }

            Hanabi-Small : {
                "colors": 2,
                "ranks": 5,
                "players": 2,
                "max_information_tokens": 3
                "hand_size": 2,
                "max_life_tokens": 1
                "observation_type": 1}

            Hanabi-Very-Small : {
                "colors": 1,
                "ranks": 5,
                "players": 2,
                "max_information_tokens": 3
                "hand_size": 2,
                "max_life_tokens": 1
                "observation_type": 1}

        """
        EzPickle.__init__(
            self,
            colors,
            ranks,
            players,
            hand_size,
            max_information_tokens,
            max_life_tokens,
            observation_type,
            random_start_player,
            render_mode,
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
        self.hanabi_env: HanabiEnv = HanabiEnv(config=self._config)

        # List of agent names
        self.agents = [f"player_{i}" for i in range(self.hanabi_env.players)]
        self.possible_agents = self.agents[:]

        self.agent_selection: str

        # Sets hanabi game to clean state and updates all internal dictionaries
        self.reset()

        # Set action_spaces and observation_spaces based on params in hanabi_env
        self.action_spaces = {
            name: spaces.Discrete(self.hanabi_env.num_moves()) for name in self.agents
        }
        self.observation_spaces = {
            player_name: spaces.Dict(
                {
                    "observation": spaces.Box(
                        low=0,
                        high=1,
                        shape=(self.hanabi_env.vectorized_observation_shape()[0],),
                        dtype=np.float32,
                    ),
                    "action_mask": spaces.Box(
                        low=0,
                        high=1,
                        shape=(self.hanabi_env.num_moves(),),
                        dtype=np.int8,
                    ),
                }
            )
            for player_name in self.agents
        }

        self.render_mode = render_mode

    def observation_space(self, agent):
        return self.observation_spaces[agent]

    def action_space(self, agent):
        return self.action_spaces[agent]

    def seed(self, seed=None):
        config = dict(seed=seed, **self._config)
        self.hanabi_env = HanabiEnv(config=config)

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

        elif not (0 <= observation_type <= 1):
            raise ValueError(
                f"Config parameter {observation_type} is out of bounds. See description in hanabi.py."
            )

    @property
    def observation_vector_dim(self):
        return self.hanabi_env.vectorized_observation_shape()

    @property
    def legal_moves(self) -> List[int]:
        return self.infos[self.agent_selection]["legal_moves"]

    @property
    def all_moves(self) -> List[int]:
        return list(range(0, self.hanabi_env.num_moves()))

    # ToDo: Fix Return value
    def reset(self, seed=None, return_info=False, options=None):
        """Resets the environment for a new game and returns observations of current player as List of ints.

        Returns:
            observation: Optional list of integers of length self.observation_vector_dim, describing observations of
            current agent (agent_selection).
        """
        if seed is not None:
            self.seed(seed=seed)

        self.agents = self.possible_agents[:]
        # Reset underlying hanabi reinforcement learning environment
        obs = self.hanabi_env.reset()

        # Reset agent and agent_selection
        self._reset_agents(player_number=obs["current_player"])

        self.rewards = {agent: 0 for agent in self.agents}
        self._cumulative_rewards = {name: 0 for name in self.agents}
        # Reset internal state
        self._process_latest_observations(obs=obs)

    def _reset_agents(self, player_number: int):
        """Rearrange self.agents as pyhanabi starts a different player after each reset()."""
        # Shifts self.agents list as long order starting player is not according to player_number
        while not self.agents[0] == "player_" + str(player_number):
            self.agents = self.agents[1:] + [self.agents[0]]

        # Agent order list, on which the agent selector operates on.
        self._agent_selector = agent_selector(self.agents)

        # Reset agent_selection
        self.agent_selection = self._agent_selector.reset()

    def _step_agents(self):
        self.agent_selection = self._agent_selector.next()

    def step(
        self, action: int, observe: bool = True, as_vector: bool = True
    ) -> Optional[Union[np.ndarray, List[List[dict]]]]:
        """Advances the environment by one step. Action must be within self.legal_moves, otherwise throws error.

        Returns:
            observation: Optional List of new observations of agent at turn after the action step is performed.
            By default a list of integers, describing the logic state of the game from the view of the agent.
            Can be a returned as a descriptive dictionary, if as_vector=False.
        """
        if (
            self.terminations[self.agent_selection]
            or self.truncations[self.agent_selection]
        ):
            return self._was_dead_step(action)
        action = int(action)

        agent_on_turn = self.agent_selection

        if action not in self.legal_moves:
            raise ValueError(
                "Illegal action. Please choose between legal actions, as documented in dict self.infos"
            )

        else:
            # Iterate agent_selection
            self._step_agents()

            # Apply action
            all_observations, reward, done, _ = self.hanabi_env.step(action=action)

            # Update internal state
            self._process_latest_observations(
                obs=all_observations, reward=reward, done=done
            )

            # sets current reward for 0 to initialize reward accumulation
            self._cumulative_rewards[agent_on_turn] = 0
            self._accumulate_rewards()

    def observe(self, agent_name: str):
        observation = (
            np.array(self.infos[agent_name]["observations_vectorized"], np.float32)
            if agent_name in self.infos
            else np.zeros_like(self.observation_spaces[agent_name].low)
        )

        legal_moves = self.infos[agent_name]["legal_moves"]
        action_mask = np.zeros(self.hanabi_env.num_moves(), "int8")
        for i in legal_moves:
            action_mask[i] = 1

        return {"observation": observation, "action_mask": action_mask}

    def _process_latest_observations(
        self, obs: Dict, reward: Optional[float] = 0, done: Optional[bool] = False
    ):
        """Updates internal state."""
        self.latest_observations = obs
        self.rewards = {a: reward for a in self.agents}
        self.terminations = {player_name: done for player_name in self.agents}
        self.truncations = {player_name: done for player_name in self.agents}

        # Here we have to deal with the player index with offset = 1
        self.infos = {
            player_name: dict(
                legal_moves=self.latest_observations["player_observations"][
                    int(player_name[-1])
                ]["legal_moves_as_int"],
                # legal_moves_as_dict=self.latest_observations['player_observations'][int(player_name[-1])]['legal_moves'],
                observations_vectorized=self.latest_observations["player_observations"][
                    int(player_name[-1])
                ]["vectorized"],
                # observations=self.latest_observations['player_observations'][int(player_name[-1])
            )
            for player_name in self.agents
        }

    def render(self):
        """Prints player's data.

        Supports console print only.
        """
        if self.render_mode is None:
            gymnasium.logger.warn(
                "You are calling render method without specifying any render mode."
            )
            return

        player_data = self.latest_observations["player_observations"]
        print(
            "Active player:",
            self.possible_agents[player_data[0]["current_player_offset"]],
        )
        for i, d in enumerate(player_data):
            print(self.possible_agents[i])
            print("========")
            print(d["pyhanabi"])
            print()

    def close(self):
        pass
