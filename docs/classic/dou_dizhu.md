---
actions: "Discrete"
title: "Dou Dizhu"
agents: "3"
manual-control: "No"
action-shape: "Discrete(27472)"
action-values: "Discrete(27472)"
observation-shape: "(901,),(790,)"
observation-values: "[0,1]"
import: "from pettingzoo.classic import dou_dizhu_v4"
agent-labels: "agents= ['landlord_0', 'peasant_0', 'peasant_1']"
---

<div class="docu-info" markdown="1">
{% include info_box.md %}
</div>

<div class="docu-content" markdown="1">
<div class="appear_big env-title" markdown="1">
{% include env_icon.md %}
## {{page.title}}
</div>




Dou Dizhu, or *Fighting the Landlord*, is a shedding game involving 3 players and a deck of cards plus 2 jokers with suits being irrelevant. Heuristically, one player is designated the "Landlord" and the others become the "Peasants". The objective of the game is to be the first one to have no cards left. If the first person to have no cards left is part of the "Peasant" team, then all members of the "Peasant" team receive a reward (+1). If the "Landlord" wins, then only the "Landlord" receives a reward (+1).

The "Landlord" plays first by putting down a combination of cards. The next player, may pass or put down a higher combination of cards that beat the previous play.

Our implementation wraps [RLCard](http://rlcard.org/games.html#dou-dizhu) and you can refer to its documentation for additional details. Please cite their work if you use this game in research.

### Arguments

``` python
dou_dizhu_v4.env(opponents_hand_visible=False)
```

`opponents_hand_visible`:  Set to `True` to observe the entire observation space as described in `Observation Space` below. Setting it to `False` will remove any observation of the opponent' hands.

### Observation Space

The observation is a dictionary which contains an `'observation'` element which is the usual RL observation described below, and an  `'action_mask'` which holds the legal moves, described in the Legal Actions Mask section.

The main *Observation Space* is encoded in a 1D vector with different concatenated features depending on the agent. To represent a combination of cards a 54-dimensional one-hot vector is encoded as follows. A 4x15 is constructed, where each column represents the rank of the cards (including the two jokers), and each row the number of matching card rank. The matrix is constructed using one-hot encoding. Since there are two jokers in the deck, the six entries that are always zero in the columns of the jokers are removed. Finally, to form the 54-dimensional vector, the one-hot matrix is flatten.
The columns and rows of the 4x15 matrix are encoded as follows:
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

The obsesrvation space of the landlord and the two peasants have different dimensions. The different agent observation spaces encode the following features:

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

#### Legal Actions Mask

The legal moves available to the current agent are found in the `action_mask` element of the dictionary observation. The `action_mask` is a binary vector where each index of the vector represents whether the action is legal or not. The `action_mask` will be all zeros for any agent except the one whose turn it is. Taking an illegal move ends the game with a reward of -1 for the illegally moving agent and a reward of 0 for all other agents.


### Action Space

The raw size of the action space of Dou Dizhu is 27,472. As a reminder, suits are irrelevant in Dou Dizhu.

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

### Version History

* v4: Upgrade to RLCard 1.0.3 (major changes to observation and action space) (1.11.0)
* v3: Fixed bug in arbitrary calls to observe() (1.8.0)
* v2: Bumped RLCard version, bug fixes, legal action mask in observation replaced illegal move list in infos (1.5.0)
* v1: Bumped RLCard version, fixed observation space, adopted new agent iteration scheme where all agents are iterated over after they are done (1.4.0)
* v0: Initial versions release (1.0.0)
</div>