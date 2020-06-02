
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

The observation space of an agent is a 373 sized vector representing the life and info tokens left, the currently constructed fireworks, the hands of all other agents, the current deck size and the discarded cards. The observation vector contains the following features, life tokens, information tokens, number of players, deck size, formed fireworks, legal moves, observed hands, discard pile, the hints received from other players, which are then serialized into a bit string.

#### Action Space

The action space is a scalar value, which ranges from 0 to the max number of actions. The values represent all possible actions a player can make, legal or not. Each possible move in the environment is mapped to a UUID, which ranges from 0 to the max number of moves. By default the max number of moves is 14. The first range of actions are to discard a card in the agent's hand. If there are k cards in the player's hand, then the first k action values are to discard one of those cards. The next k actions would be to play one of the cards in the player's hand. Finally, the remaining actions are to reveal a color or rank in another players hand. The first set of reveal actions would be revealing all colors or values of cards for the next player in order, and this repeats for all the other players in the environment.

#### Rewards

The reward of each step is calculated as the change in game score from the last step. The game score is 0 until the terminal state. Once the game has ended, the total score is calculated as the sum of values in each constructed firework.

