---
layout: "docu"
title: "Gin Rummy"
actions: "Discrete"
agents: "2"
manual-control: "No"
action-shape: "Discrete(110)"
action-values: "Discrete(110)"
observation-shape: "(5, 52)"
observation-values: "[0,1]"
num-states: "10^52"
import: "from pettingzoo.classic import gin_rummy_v4"
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

The observation is a dictionary which contains an `'obs'` element which is the usual RL observation described below, and an  `'action_mask'` which holds the legal moves, described in the Legal Actions Mask section.

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

The legal moves available to the current agent are found in the `action_mask` element of the dictionary observation. The `action_mask` is a binary vector where each index of the vector represents whether the action is legal or not. The `action_mask` will be all zeros for any agent except the one whose turn it is. Taking an illegal move ends the game with a reward of -1 for the illegally moving agent and a reward of 0 for all other agents.

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
</div>