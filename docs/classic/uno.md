---
actions: "Discrete"
title: "Uno"
agents: "2"
manual-control: "No"
action-shape: "Discrete(61)"
action-values: "Discrete(61)"
observation-shape: "(7, 4, 15)"
observation-values: "[0, 1]"
import: "from pettingzoo.classic import uno_v4"
agent-labels: "agents= ['player_0', 'player_1']"
---

<div class="docu-info" markdown="1">
{% include info_box.md %}
</div>

<div class="docu-content" markdown="1">
<div class="appear_big env-title" markdown="1">
{% include env_icon.md %}
## {{page.title}}
</div>




Uno is shedding game involving 2 players. At the beginning, each player receives 7 cards and the winner is the first player with no cards left. In order to discard a card from their hand, a player must match either the color or number of the card on top of the discard pile. If the player does not have a card to discard, then they will take a card from the draw pile. The deck of cards include 4 colors (blue, green, yellow, and red), 10 numbers (0 to 9), and special cards (Wild, Wild Draw Four, Draw Two, Skip, and Reverse).

Our implementation wraps [RLCard](http://rlcard.org/games.html#uno) and you can refer to its documentation for additional details. Please cite their work if you use this game in research.

### Arguments

``` python
uno_v4.env(opponents_hand_visible=False)
```

`opponents_hand_visible`:  Set to `True` to observe the entire observation space as described in `Observation Space` below. Setting it to `False` will remove any observation of the opponent' hands and the observation space will only include planes 0 to 3.

### Observation Space

The observation is a dictionary which contains an `'obs'` element which is the usual RL observation described below, and an  `'action_mask'` which holds the legal moves, described in the Legal Actions Mask section.

The main observation space has a shape of (7, 4, 15). Planes 0-2 represent the current player's hand, while planes 4-6 represent the opponent's hand. For these sets of planes, the first index indicates the number of copies of a card, the second index the color, and the last index the card number (including any special cards). Uno is played with 2 identical decks, so a player can have 0, 1, or 2 copies of a given card, which is why each player has 3 planes to represent their hand.

| Plane | Feature                                                     |
| :---: | ----------------------------------------------------------- |
|   0   | Cards that the current player has 0 copies of in their hand |
|   1   | Cards that the current player has 1 copy of in their hand   |
|   2   | Cards that the current player has 2 copies of in their hand |
|   3   | Target card (top of the Discard pile)                       |
|   4   | Cards that the opponent has 0 copies of in their hand       |
|   5   | Cards that the opponent has 1 copy of in their hand         |
|   6   | Cards that the opponent has 2 copies of in their hand       |

#### Encoding per Plane

| Plane Row Index | Description |
|:---------------:|-------------|
|        0        | Red         |
|        1        | Green       |
|        2        | Blue        |
|        3        | Yellow      |

| Plane Column Index | Description    |
|:------------------:|----------------|
|        0           | 0              |
|        1           | 1              |
|        2           | 2              |
|       ...          | ...            |
|        9           | 9              |
|        10          | Wild           |
|        11          | Wild Draw Four |
|        12          | Skip           |
|        13          | Draw Two       |
|        14          | Reverse        |

#### Legal Actions Mask

The legal moves available to the current agent are found in the `action_mask` element of the dictionary observation. The `action_mask` is a binary vector where each index of the vector represents whether the action is legal or not. The `action_mask` will be all zeros for any agent except the one whose turn it is. Taking an illegal move ends the game with a reward of -1 for the illegally moving agent and a reward of 0 for all other agents.

### Action Space

The action space is as described by RLCards.

| Action ID |                                     Action                                     |
|:---------:| ------------------------------------------------------------------------------ |
|  0 - 9    | Red number cards<br>_`0`: 0-Red, `1`: 1-Red, ..., `9`: 9-Red_                  |
| 10 - 12   | Red action cards<br>_`10`: Skip, `11`: Reverse, `12`: Draw 2_                  |
|     13    | Red "Wild" card                                                                |
|     14    | Red "Wild and Draw 4" card                                                     |
| 15 - 24   | Green number cards<br>_`15`: 0-Green, `16`: 1-Green, ..., `24`: 9-Green_       |
| 25 - 27   | Green action cards<br>_`25`: Skip, `26`: Reverse, `27`: Draw 2_                |
|     28    | Green "Wild" card                                                              |
|     29    | Green "Wild and draw 4" card                                                   |
| 30 - 39   | Blue number cards<br>_`30`: 0-Blue, `31`: 1-Blue, ..., `39`: 9-Blue_           |
| 40 - 42   | Blue action cards<br>_`40`: Skip, `41`: Reverse, `42`: Draw 2_                 |
|     43    | Blue "Wild" card                                                               |
|     44    | Blue "Wild and Draw 4" card                                                    |
| 45 - 54   | Yellow number cards<br>_`45`: 0-Yellow, `46`: 1-Yellow, ..., `54`: 9-Yellow_   |
| 55 - 57   | Yellow action cards<br>_`55`: Skip, `56`: Reverse, `57`: Draw 2_               |
|     58    | Yellow "Wild" card                                                             |
|     59    | Yellow "Wild and Draw 4" card                                                  |
|     60    | Draw                                                                           |

For example, you would use action `6` to put down a red "6" card or action `60` to draw a card.

### Rewards

| Winner | Loser |
| :----: | :---: |
| +1     | -1    |

### Version History

* v4: Upgrade to RLCard 1.0.3 (1.11.0)
* v3: Fixed bug in arbitrary calls to observe() (1.8.0)
* v2: Bumped RLCard version, bug fixes, legal action mask in observation replaced illegal move list in infos (1.5.0)
* v1: Bumped RLCard version, fixed observation space, adopted new agent iteration scheme where all agents are iterated over after they are done (1.4.0)
* v0: Initial versions release (1.0.0)
</div>