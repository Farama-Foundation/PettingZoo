# pistonBall
This is a simple game written in Python3, where the goal is to move the ball to the left wall of the game border by activating any of the twenty pistons (pistons move vertically only).

The file `pistonBall.py` contains the necessary class definition and methods to run the game. The game is written in a way that it can be learned by a Reinforcement Learning algorithm that makes calls to the [Gym API](https://gym.openai.com/). The game uses `pymunk`, a pythonic 2-D physics library, to model the interaction between the pistons and the ball and also the movement of the ball. `pygame` package is used to display the game elements on the screen.

`humanGame.py` lets a human play the game. Keys *a* and *d* control which piston is selected to move (initially the rightmost piston is selected) and keys *w* and *s* control how far the selected piston moves in the vertical direction.

## Requirements
`ray`, `gym`, `pygame`, `pymunk`, `scikit-image` and `numpy`.
These dependencies can be installed by using the command `pip install -r requirements.txt`
