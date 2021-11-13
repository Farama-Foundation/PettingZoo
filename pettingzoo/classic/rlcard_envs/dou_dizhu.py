import random

import numpy as np
import rlcard
from gym import spaces

from pettingzoo import AECEnv
from pettingzoo.utils import wrappers
from pettingzoo.utils.agent_selector import agent_selector

from .rlcard_base import RLCardBase

"""
Dou Dizhu, or *Fighting the Landlord*, is a shedding game involving 3 players and a deck of cards plus 2 jokers with suits being irrelevant. Heuristically, one player is designated the "Landlord" and the others become the "Peasants". The objective of the game is to be the first one to have no cards left. If the first person to have no cards left is part of the "Peasant" team, then all members of the "Peasant" team receive a reward (+1). If the "Landlord" wins, then only the "Landlord" receives a reward (+1).

The "Landlord" plays first by putting down a combination of cards. The next player, may pass or put down a higher combination of cards that beat the previous play.

Our implementation wraps [RLCard](http://rlcard.org/games.html#dou-dizhu) and you can refer to its documentation for additional details. Please cite their work if you use this game in research.

### Arguments

`opponents_hand_visible`:  Set to `True` to observe the entire observation space as described in `Observation Space` below. Setting it to `False` will remove any observation of the opponent' hands.

### Observation Space

##### Encoding per Plane
| Plane Row Index |          Description          |
|:---------------:| ----------------------------- |
|        0        | 0 matching cards of same rank |
|        1        | 1 matching cards of same rank |
|        2        | 2 matching cards of same rank |
|        3        | 3 matching cards of same rank |
|        4        | 4 matching cards of same rank |

| Plane Column Index | Description |
|:------------------:|-------------|
|          0         | 3           |
|          1         | 4           |
|         ...        | ...         |
|          7         | 10          |
|          8         | Jack        |
|          9         | Queen       |
|         10         | King        |
|         11         | Ace         |
|         12         | 2           |
|         13         | Black Joker |
|         14         | Red Joker   |

##### Landlord Observation

|             Feature            | Feature Index |          Description          |
|--------------------------------|:-------------:| ----------------------------- |
|                 `current_hand` |     [0:53]    | Current landlord's hand as a 54-dimensional one-hot vector |
|                  `others_hand` |    [54:107]   | Other players hand (if `opponents_hand_visible`) |
|                  `last_action` |   [108:161]   | The most recent action as a 54-dimensional one-hot vector |
|               `last_9_actions` |   [162:647]   | The most recent 9 actions |
|     `landlord_up_played_cards` |   [648:701]   | The union of all the cards played by the player that acts before the landlord as a 54-dimensional one-hot vector |
|   `landlord_down_played_cards` |   [702:755]   | The union of all the cards played by the player that acts after the landlord as a 54-dimensional one-hot vector |
|   `landlord_up_num_cards_left` |   [756:772]   | Number of cards left for the peasant player that plays before the landlord |
| `landlord_down_num_cards_left` |   [773:789]   | Number of cards left for the peasant player that plays after the landlord |

##### Peasant Observation

|             Feature            | Feature Index |          Description          |
|--------------------------------|:-------------:| ----------------------------- |
|                 `current_hand` |     [0:53]    | Current landlord's hand as a 54-dimensional one-hot vector |
|                  `others_hand` |    [54:107]   | Other players hand (if `opponents_hand_visible`) |
|                  `last_action` |   [108:161]   | The most recent action as a 54-dimensional one-hot vector |
|               `last_9_actions` |   [162:647]   | The most recent 9 actions |
|        `landlord_played_cards` |   [648:701]   | The union of all the cards played by the landlord |
|        `teammate_played_cards` |   [702:755]   | The union of all the cards played by the other peasant agent |
|         `last_landlord_action` |   [756:809]   | The last action played by the landlord |
|         `last_teammate_action` |   [810:863]   | The last action played by the other peasant agent |
|      `landlord_num_cards_left` |   [864:883]   | Number of cards left for the landlord |
|      `teammate_num_cards_left` |   [884:900]   | Number of cards left for the other peasant agent |

### Action Space
| Action Type      | Description                                                  | Action ID | Example                                                      |
| ---------------- | ----------------------------------- | :---------: | ------------------------------------------------------------ |
| Solo             | Any single card                                              | 0-14      | `0`: 3, `1`: 4, ..., `12`: 2, `13`: Black Joker, `14`: Red Joker |
| Pair             | Two matching cards of equal rank                             | 15-27     | `15`: 33, `16`: 44, ..., `25`: KK, `26`: AA, `27`: 22        |
| Trio             | Three matching cards of equal rank                           | 28-40     | `28`: 333, `29`: 444, ..., `38`: KKK, `39`: AAA, `40`: 222   |
| Trio with single | Three matching cards of equal rank + single card as the kicker (e.g. 3334) | 41-222     | `41`: 3334, `42`: 3335, ..., `220`: A222, `221`: 222B, `222`: 222R |
| Trio with pair   | Three matching cards of equal rank + pair of cards as the kicker (e.g. 33344) | 223-378     | `223`: 33344, `224`: 33355, ..., `376`: QQ222, `377`: KK222, `378`: AA222 |
| Chain of solo    | At least five consecutive solo cards                         | 379-414    | `379`: 34567, `380`: 45678, ..., `412`: 3456789TJQK, `413`: 456789TJQKA, `414`: 3456789TJQKA |
| Chain of pair    | At least three consecutive pairs                             | 415-466   | `415`: 334455, `416`: 445566, ..., `464`: 33445566778899TTJJQQ, `465`: 445566778899TTJJQQKK, `466`: 5566778899TTJJQQKKAA |
| Chain of trio    | At least two consecutive trios                               | 467-511   | `467`: 333444, `467`: 444555, ..., `509`: 777888999TTTJJJQQQ, `510`: 888999TTTJJJQQQKKK, `511`: 999TTTJJJQQQKKKAAA |
| Plane with solo  | Two consecutive trios + a distinct kicker for each trio (e.g. 33344456) | 512-22333   | `512`: 33344455, `513`: 33344456, ..., `22331`: 899TTTJJJQQQKKKAAA22, `22332`: 89TTTJJJQQQKKKAAA222, `22333`: 99TTTJJJQQQKKKAAA222 |
| Plane with pair  | Two consecutive trios + 2 distinct pairs (e.g. 3334445566)   | 22334-25272   | `22334`: 3334445566, `22335`: 3334445577, ..., `25270`: 7788TTJJJQQQKKKAAA22, `25271`: 7799TTJJJQQQKKKAAA22, `25272`: 8899TTJJJQQQKKKAAA22 |
| Quad with solo   | Four matching cards of equal rank + 2 distinct solo cards (e.g 333345) | 25273-26598   | `25273`: 333344, `25274`: 333345, ..., `26596`: AA2222, `26597`: A2222B, `26598`: A2222R |
| Quad with pair   | Four matching cards of equal rank + 2 distinct pairs (e.g 33334455) | 26599-27456   | `26599`: 33334455, `26600`: 33334466, ..., `27454`: QQKK2222, `27455`: QQAA2222, `27456`: KKAA2222 |
| Bomb             | Four matching cards of equal rank                            | 27457-275469   | `27457`: 3333, `27458`: 4444, ..., `275467`: KKKK, `275468`: AAAA, `275469`: 2222 |
| Rocket           | Black Joker + Red Joker                                      | 275470       | `275470`: Black Joker (B) + Red Joker (R)                       |
| Pass             | Pass                                                         | 275471       | `275471`: Pass                                                  |

### Rewards

We modified the reward structure compared to RLCard. Instead of rewarding `0` to the losing player, we assigned a `-1` reward to the losing agent.

| Winner | Loser |
| :----: | :---: |
| +1     |   -1  |
"""

def env(**kwargs):
    env = raw_env(**kwargs)
    env = wrappers.CaptureStdoutWrapper(env)
    env = wrappers.TerminateIllegalWrapper(env, illegal_reward=-1)
    env = wrappers.AssertOutOfBoundsWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env


class raw_env(RLCardBase):

    metadata = {'render.modes': ['human'], "name": "dou_dizhu_v4"}

    def __init__(self, opponents_hand_visible=False):
        self._opponents_hand_visible = opponents_hand_visible
        self.agents = ['landlord_0', 'peasant_0', 'peasant_1']
        obs_dimension = 901 if self._opponents_hand_visible else 847
        super().__init__("doudizhu", 3, (obs_dimension, ))
        self.observation_spaces = self._convert_to_dict([spaces.Dict(
            {'observation': spaces.Box(low=0.0, high=1.0, shape=(obs_dimension - 111, )
             if agent == 'landlord_0' else (obs_dimension, ), dtype=self._dtype),
             'action_mask': spaces.Box(low=0, high=1, shape=(self.env.num_actions,), dtype=np.int8)})
             for agent in self.agents])

    def _scale_rewards(self, reward):
        # Maps 1 to 1 and 0 to -1
        return 2 * reward - 1

    def observe(self, agent):
        obs = self.env.get_state(self._name_to_int(agent))
        if self._opponents_hand_visible:
            observation = obs['obs'].astype(self._dtype)
        else:
            observation = np.delete(obs['obs'], range(54, 108)).astype(self._dtype)

        legal_moves = self.next_legal_moves
        action_mask = np.zeros(27472, 'int8')
        for i in legal_moves:
            action_mask[i] = 1

        return {'observation': observation, 'action_mask': action_mask}

    def render(self, mode='human'):
        for player in self.possible_agents:
            state = self.env.game.get_state(self._name_to_int(player))
            print(f"\n===== {player}'s Hand =====")
            print(state['current_hand'])
        print('\n=========== Last 3 Actions ===========')
        for action in state['trace'][:-4:-1]:
            print(f'{self._int_to_name(action[0])}: {action[1]}')
        print('\n')
