# cooperative_pong
This is a basic game of pong, written in Pygame (Python3), where the goal of both the players is to keep the ball in play for the longest time possible.

The file `cooperative_pong.py` contains the necessary class definition and methods to run the game. The game is written in a way that it can be learned by a Reinforcement Learning algorithm that makes calls to the Gym API.

`human_pong.py` lets a human play the game. Keys *w* and *s* control player1 paddle (on the left of the screen) and keys *UP* and *DOWN* control player2 paddle (on the right).

## Requirements
`ray`, `gym`, `pygame`, `scikit-image` and `numpy`.
These dependencies (including the correct versions) can be installed by using the command `pip install -r requirements.txt`
