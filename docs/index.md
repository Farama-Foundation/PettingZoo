# Environment Documentation

Supp

## Gamma Enviroments

`pettingzoo.sisl`

| Environment             | Observations | Actions    | Agents | Manual Control |
|-------------------------|--------------|------------|--------|----------------|
| Cooperative Pong        | Graphical    | Discrete   |   2    | Yes            |
| Knights Archers Zombies |  Graphical   | Discrete   | 4 (+/-)| Yes             |
| Pistonball              | Graphical    |   Either     |   20   | Yes            |
| Prison                  |     Either     |   Either     |   8    | Yes            |
| Prospector              |    Graphical | Continuous | 4 (+/-)| Yes            |


### Cooperative Pong

| Observations | Actions    | Agents | Manual Control |
|--------------|------------|--------|----------------|
| Graphical    | Discrete   |   2    | Yes            |

`pettingzoo.gamma.cooperative_pong`

*image*

*blurb*

*arguments*

*about arguments*

Leaderboard:

| Average Total Reward | Method | Institutions | Paper | Code |
|----------------------|--------|--------------|-------|------|
|  x                   | x      | x            |   x   |   x  |

### Knights Archers Zombies ('KAZ')

| Observations | Actions    | Agents | Manual Control |
|--------------|------------|--------|----------------|
|  Graphical   | Discrete   | 4 (+/-)| No             |

`pettingzoo.gamma.knights_archers_zombies`

### Pistonball

| Environment             | Observations | Actions    | Agents | Manual Control |
|-------------------------|--------------|------------|--------|----------------|
| Pistonball              | Graphical    |   Either     |   20   | Yes            |

`pettingzoo.gamma.pistonball`

*image*

*blurb*

*arguments*

*about arguments*

Leaderboard:

| Average Total Reward | Method | Institutions | Paper | Code |
|----------------------|--------|--------------|-------|------|
|  x                   | x      | x            |   x   |   x  |

### Prison

| Observations | Actions    | Agents | Manual Control |
|--------------|------------|--------|----------------|
| Either         |   Either     |   8    | Yes            |

`pettingzoo.gamma.prison`

*image*

*blurb*

*arguments*

*about arguments*

Discrete Leaderboard:

| Average Total Reward | Method | Institutions | Paper | Code |
|----------------------|--------|--------------|-------|------|
|  x                   | x      | x            |   x   |   x  |

Continuous Leaderboard:

| Average Total Reward | Method | Institutions | Paper | Code |
|----------------------|--------|--------------|-------|------|
|  x                   | x      | x            |   x   |   x  |

### Prospector

| Observations | Actions    | Agents | Manual Control |
|--------------|------------|--------|----------------|
|    Graphical | Continuous | 4 (+/-)| Yes            |

`pettingzoo.gamma.prospector`

*image*

*blurb*

*arguments*

*about arguments*

Leaderboard:

| Average Total Reward | Method | Institutions | Paper | Code |
|----------------------|--------|--------------|-------|------|
|  x                   | x      | x            |   x   |   x  |


## SISL Enviroments

`pettingzoo.sisl`

| Environment             | Observations | Actions    | Agents | Manual Control |
|-------------------------|--------------|------------|--------|----------------|
| Multiant                | ?            | Continuous |   ?    | No             |
| Multiwalker             |  Vector    (viewable)  | Discrete   | 3 (+/-)| No             |
| Pursuit                 | Graphical    |   Either     | 8 (+/-)| No             |
| Waterworld              |     Vector (viewable)   |   Either     | 3 (+/-)| No             |

Please additionally cite 

```
@inproceedings{gupta2017cooperative,
  title={Cooperative multi-agent control using deep reinforcement learning},
  author={Gupta, Jayesh K and Egorov, Maxim and Kochenderfer, Mykel},
  booktitle={International Conference on Autonomous Agents and Multiagent Systems},
  pages={66--83},
  year={2017},
  organization={Springer}
}
```

### Multiant

| Observations | Actions    | Agents | Manual Control |
|--------------|------------|--------|----------------|
| ?            | Continuous |   ?    | No             |

`pettingzoo.sisl.multiant`

*image*

*blurb*

*arguments*

*about arguments*

Leaderboard:

| Average Total Reward | Method | Institutions | Paper | Code |
|----------------------|--------|--------------|-------|------|
|  x                   | x      | x            |   x   |   x  |

Add Gupta et al and DDPG paper results too

### Multiwalker

| Observations | Actions    | Agents | Manual Control |
|--------------|------------|--------|----------------|
|  Vector      | Discrete   | 3 (+/-)| No             |

`pettingzoo.sisl.multiwalker`

*image*

A package is placed on top of (by default) 3 pairs of robot legs which you control. The robots must learn to move the package as far as possible to the right. Each walker gets a reward of 1 for moving the package forward, and a reward of -100 for dropping the package. Each walker exerts force on two joints in their two legs, giving a continuous action space represented as a 4 element vector. Each walker observes via a 32 element vector, containing simulated noisy lidar data about the environment and information about neighboring walkers.

*arguments*

*about arguments*

Leaderboard:

| Average Total Reward | Method | Institutions | Paper | Code |
|----------------------|--------|--------------|-------|------|
|  x                   | PPO    | UMD          |       |      |

Add Gupta et al and DDPG paper results too

### Pursuit

| Observations | Actions    | Agents | Manual Control |
|--------------|------------|--------|----------------|
| Graphical    |   Either   | 8 (+/-)| No             |

`pettingzoo.sisl.pursuit`

*image*

By default there are 30 blue evaders and 8 red pursuer agents, in a 16 x 16 grid with an obstacle in the center, shown in white. The evaders move randomly, and the pursuers are controlled. Every time the pursuers fully surround an evader, each of the surrounding agents receives a reward of 5, and the evader is removed from the environment. Pursuers also receive a reward of 0.01 every time they touch an evader. The pursuers have a discrete action space of up, down, left, right and stay. Each pursuer observes a 7 x 7 grid centered around itself, depicted by the orange boxes surrounding the red pursuer agents. The enviroment runs for 500 frames.

*arguments*

*about arguments*

Leaderboard:

| Average Total Reward | Method | Institutions | Paper | Code |
|----------------------|--------|--------------|-------|------|
|  x                   | PPO    | UMD          |       |      |

Add Gupta et al and DDPG paper results too

### Waterworld

| Observations | Actions    | Agents | Manual Control |
|--------------|------------|--------|----------------|
|     Vector (viewable)   |   Either     | 3 (+/-)| No             |

`pettingzoo.sisl.waterworld`

*image*

By default there are 5 agents (purple), 5 food targets (green) and 10 poison targets (red). Each agent has 30 range-limited sensors, depicted by the black lines, to detect neighboring agents, food and poison targets, resulting in 212 long vector of computed values about the environment for the observation space. They have a continuous action space represented as a 2 element vector, which corresponds to left/right and up/down thrust. The agents each receive a reward of 10 when more than one agent captures food together (the food is not destroyed), a shaping reward of 0.01 for touching food, a reward of -1 for touching poison, and a small negative reward when two agents collide based on the force of the collision. The enviroment runs for 500 frames.

*arguments*

*about arguments*

Leaderboard:

| Average Total Reward | Method | Institutions | Paper | Code |
|----------------------|--------|--------------|-------|------|
|  x                   | PPO    | UMD          |       |      |

Add Gupta et al and DDPG paper results too


## Other Enviroments

`pettingzoo.other_envs`

| Environment             | Observations | Actions    | Agents | Manual Control |
|-------------------------|--------------|------------|--------|----------------|
| Rock Paper Scissors                | Vector            | Discrete |   2    | No             |
| Rock Paper Scissors Lizard Spock     |  Vector    (  | Discrete   | 2 | No             |

### Rock Paper Scissors

| Observations | Actions    | Agents | Manual Control |
|--------------|------------|--------|----------------|
| Vector            | Discrete |   2    | No             |

`pettingzoo.other_envs.rps`

*blurb*

*arguments*

*about arguments*


### Rock Paper Scissors Lizard Spock

| Observations | Actions    | Agents | Manual Control |
|--------------|------------|--------|----------------|
|  Vector      | Discrete   | 2 | No             |

`pettingzoo.other_envs.rpsls`

*blurb*

*arguments*

*about arguments*
