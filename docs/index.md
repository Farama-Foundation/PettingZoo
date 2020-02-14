# Environment Documentation

Please cite

## Gamma

`pettingzoo.sisl`

| Environment             | Observations | Actions    | Agents |
|-------------------------|--------------|------------|--------|
| Cooperative Pong        | Graphical    | Discrete   |   2    |
| Knights Archers Zombies |  Graphical   | Discrete   | 4 (+/-)|
| Pistonball              | Graphical    |   Both     |   20   |
| Prison                  |     Both     |   Both     |   20   |
| Prospector              |    Graphical | Continuous | 4 (+/-)|


### Cooperative Pong

`pettingzoo.gamma.cooperative_pong`

Image

Arguments

About arguments

Blurb

Cite

Leaderboard

### Knights Archers Zombies ('KAZ')

`pettingzoo.gamma.knights_archers_zombies`

### Pistonball

`pettingzoo.gamma.pistonball`

### Prison

`pettingzoo.gamma.prison`

### Prospector

`pettingzoo.gamma.prospector`


## SISL

`pettingzoo.sisl`

| Environment             | Observations | Actions    | Agents |
|-------------------------|--------------|------------|--------|
| Multiant                | ?            | Continuous |   ?    |
| Multiwalker             |  Vector      | Discrete   | 3 (+/-)|
| Pursuit                 | Graphical    |   Both     | 8 (+/-)|
| Waterworld              |     Vector   |   Both     | 3 (+/-)|

### Multiant

`pettingzoo.sisl.multiant`

### Multiwalker

`pettingzoo.sisl.multiwalker`

*image*

A package is placed on top of (by default) 3 pairs of robot legs which you control. The robots must learn to move the package as far as possible to the right. Each walker gets a reward of 1 for moving the package forward, and a reward of -100 for dropping the package. Each walker exerts force on two joints in their two legs, giving a continuous action space represented as a 4 element vector. Each walker observes via a 32 element vector, containing simulated noisy lidar data about the environment and information about neighboring walkers.

### Pursuit

`pettingzoo.sisl.pursuit`

*image*

By default there are 30 blue evaders and 8 red pursuer agents, in a 16 x 16 grid with an obstacle in the center, shown in white. The evaders move randomly, and the pursuers are controlled. Every time the pursuers fully surround an evader, each of the surrounding agents receives a reward of 5, and the evader is removed from the environment. Pursuers also receive a reward of 0.01 every time they touch an evader. The pursuers have a discrete action space of up, down, left, right and stay. Each pursuer observes a 7 x 7 grid centered around itself, depicted by the orange boxes surrounding the red pursuer agents. The enviroment runs for 500 frames.

### Waterworld

`pettingzoo.sisl.waterworld`

*image*

By default there are 5 agents (purple), 5 food targets (green) and 10 poison targets (red). Each agent has 30 range-limited sensors, depicted by the black lines, to detect neighboring agents, food and poison targets, resulting in 212 long vector of computed values about the environment for the observation space. They have a continuous action space represented as a 2 element vector, which corresponds to left/right and up/down thrust. The agents each receive a reward of 10 when more than one agent captures food together (the food is not destroyed), a shaping reward of 0.01 for touching food, a reward of -1 for touching poison, and a small negative reward when two agents collide based on the force of the collision. The enviroment runs for 500 frames.

## Other Enviroments

`pettingzoo.other_envs`

### Rock Paper Scissors

`pettingzoo.other_envs.rps`

### Rock Paper Scissors Lizard Spock

`pettingzoo.other_envs.rpsls`