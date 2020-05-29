
### Hanabi

This game part of the [classic games](../classic.md), please visit that page first for general information about these games.

| Actions  | Agents | Manual Control | Action Shape  | Action Values  | Observation Shape | Observation Values | Num States    |
|----------|--------|----------------|---------------|----------------|-------------------|--------------------|---------------|
| Discrete | 2      | No             | (1,)          | Discrete(14)   | (373,)            | [0,1]              |   ?           |

`from pettingzoo.classic import hanabi_v0`

`agents= ['player_0', 'player_0']`

*gif*

*AEC Diagram*

Hanabi is a 2-5 player cooperative game where players work together to form fireworks of different colors. A firework is a set of cards of the same color, ordered from 1 to 5. Cards in the game have both a color and number; each player can view the cards another player holds, but not their own. Players cannot directly communicate with each other, but must instead remove an info token from play in order to give information. Players can tell other players which of the cards in their hand is a specific color, or a specific number. There are initially 8 info tokens, but players can discard cards in their hand to return an info token into play. Players can also play a card from their hand: the card must either begin a new firework or be appended in order to an existing firework. However, 2 fireworks cannot have the same color, and a single firework cannot repeat numbers. If the played card does not satisfy these conditions, a life token is placed. The game ends when either 3 life tokens have been placed, all 5 fireworks have been completed, or all cards have been drawn from the deck. Points are awarded based on the largest card value in each created firework.

#### Observation Space

The observation space of an agent is a 373 sized vector representing the life and info tokens left, the currently constructed fireworks, the hands of all other agents, the current deck size and the discarded cards.

#### Action Space

The action space is a scalar value, with 14 possible values. The values represent all possible actions a player can make, legal or not. These actions are to either reveal cards of a certain color in another agent's hand, cards of a certain n umber in another agent's hand, discard a card, or to play one of their own cards.

#### Rewards

Rewards are calculated as the difference from the reward of the last state. The score is calculated at a terminal state, based on the highest value of each firework.

