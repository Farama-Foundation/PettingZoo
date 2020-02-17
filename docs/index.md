# Environment Documentation

None done:
add n inputs and output dims to tables
Add images
About arguments

Partially done:
Write pistonball and prison blurbs
Review KAZ blurb
Multiwalker arguments
Add 500 frame flag to every arguments
Review cooperative pong blurb once done

Game work:
Remove arguments that people can't use, or should never use from SISL games (ally_layer and oponent layer in pursuit?)
Handle 500 a flag in all sisl games
Move flatten functionality out of pursuit
Have multiwalker accept arguments
Add argument handling for cooperative pong, pistonball, KAZ

## Gamma Enviroments

`pettingzoo.sisl`

| Environment             | Observations | Actions    | Agents | Manual Control |
|-------------------------|--------------|------------|--------|----------------|
| Cooperative Pong        | Graphical    | Discrete   |   2    | Yes            |
| Knights Archers Zombies |  Graphical   | Discrete   | 4 (+/-)| Yes            |
| Pistonball              | Graphical    |   Either   |   20   | Yes            |
| Prison                  |     Either   |   Either   |   8    | Yes            |
| Prospector              |    Graphical | Continuous | 4 (+/-)| Yes            |


### Cooperative Pong

| Observations | Actions    | Agents | Manual Control |
|--------------|------------|--------|----------------|
| Graphical    | Discrete   |   2    | Yes            |

`pettingzoo.gamma.cooperative_pong`

*image*

*blurb*

```
cooperative_pong.env(ball_velocity=?, left_paddle_velocity=?,
right_paddle_velocity=?, wedding_cake_paddle=True, max_frames=900)
```

*about arguments*

Leaderboard:

| Average Total Reward | Method | Institution | Paper | Code |
|----------------------|--------|--------------|-------|------|
|  x                   | x      | x            |   x   |   x  |

### Knights Archers Zombies ('KAZ')

| Observations | Actions    | Agents | Manual Control |
|--------------|------------|--------|----------------|
|  Graphical   | Discrete   | 4 (+/-)| Yes            |

`pettingzoo.gamma.knights_archers_zombies`

*image*

Zombies walk from the top border of the screen down to the bottom border in unpredictable paths. The agents you control are knights and archers (default 2 knights and 2 archers) that are initially positioned at the bottom border of the screen. Each agent can rotate clockwise or counter-clockwise and move forward or backward. Each agent can also attack to kill zombies. When a knight attacks, it swings a mace in an arc in front of its current heading direction. When an archer attacks, it fires an arrow in a straight line in the direction of the archer's heading. The game ends when all agents die (collide with a zombie) or a zombie reaches the bottom screen border. An agent gets a reward when it kills a zombie. Each agent observes the environment as a square region around itself, with its own body in the center of the square. The observation is represented as a 1600-element vector (40x40 grid around the agent).

```
knights_archers_zombies.env(spawn_rate=?, knights=2, archers=2, 
killable_knights=True, killable_archers=True, line_death=True, max_frames=900)
```

*about arguments*

Leaderboard:

| Average Total Reward | Method | Institution | Paper | Code |
|----------------------|--------|--------------|-------|------|
|  x                   | x      | x            |   x   |   x  |

### Pistonball

| Environment             | Observations | Actions    | Agents | Manual Control |
|-------------------------|--------------|------------|--------|----------------|
| Pistonball              | Graphical    |   Either   |   20   | Yes            |

`pettingzoo.gamma.pistonball`

*image*

*blurb*

Arguments:

```
pistonball.env(local_ratio=.02, continuous=False, random_drop=True,
starting_angular_momentum=True, ball_mass = .75, ball.friction=.3,
ball.elasticity=1.5, max_frames=900)
```

*about arguments*

Leaderboard:

| Average Total Reward | Method | Institution | Paper | Code |
|----------------------|--------|--------------|-------|------|
|  x                   | x      | x            |   x   |   x  |

### Prison

| Observations | Actions    | Agents | Manual Control |
|--------------|------------|--------|----------------|
| Either         |   Either     |   8    | Yes            |

`pettingzoo.gamma.prison`

*image*

*blurb*

Arguments:
```
prison.env(graphical_output=True, discrete_input=True, syncronized_start=False,
max_frames=900)
```

*about arguments*

Discrete Leaderboard:

| Average Total Reward | Method | Institution | Paper | Code |
|----------------------|--------|--------------|-------|------|
|  x                   | x      | x            |   x   |   x  |

Continuous Leaderboard:

| Average Total Reward | Method | Institution | Paper | Code |
|----------------------|--------|--------------|-------|------|
|  x                   | x      | x            |   x   |   x  |

### Prospector

| Observations | Actions    | Agents | Manual Control |
|--------------|------------|--------|----------------|
|    Graphical | Continuous | 4 (+/-)| Yes            |

`pettingzoo.gamma.prospector`

*image*

This game is inspired by gold panning in the American "wild west" movies. There's a blue river at the bottom of the screen, which contains gold. 4 "panner" agents can move and touch the river and pan from it, and get a gold nugget (visibly held by them). They take a 3 element vector of continuous values (the first for forward/backward, the second for left/right movement, the third for clockwise/counter-clockwise rotation). They can only hold 1 nugget at a time.

There are a handful of bank chests at the top of the screen. The panner agents can hand their held gold nugget to the 2 "manager" agents, to get a reward. The manager agents can't rotate, and the panner agents must give the nuggets (which are held in the front of their body) to the front (always pointing upwards) of the managers. The managers then get the gold, and can deposit it into the chests to recieve a reward. They take a 2 element vector of continuous values (the first for forward/backward, the second for left/right movement). They can only hold 1 nugget at a time.

*arguments*

*about arguments*

Leaderboard:

| Average Total Reward | Method | Institution | Paper | Code |
|----------------------|--------|--------------|-------|------|
|  x                   | x      | x            |   x   |   x  |


## SISL Enviroments

`pettingzoo.sisl`

| Environment             | Observations | Actions    | Agents | Manual Control |
|-------------------------|--------------|------------|--------|----------------|
| Multiant                | ?            | Continuous |   ?    | No             |
| Multiwalker             |  Vector (viewable)  | Discrete   | 3 (+/-)| No             |
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

| Average Total Reward | Method | Institution | Paper | Code |
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

Arguments:


```
Refactor game to take arguments
```

*about arguments*

Leaderboard:

| Average Total Reward | Method | Institution | Paper | Code |
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

Arguments:

```
pursuit.env(sample_maps=False, reward_mech='local', n_evaders=30, n_pursuers=8,
obs_range=7, layer_norm=10, n_catch=2, random_opponents=False, max_opponents=10,
freeze_evaders=False, catchr=0.01, caughtr=-0.01, term_pursuit=5.0,
term_evader=-5.0, urgency_reward=0.0, include_id=True, initial_config={},
surround=True, constraint_window=1.0, cirriculum_remove_every=500,
cirriculum_constrain_rate = 0.0, cirriculum_turn_off_shaping=np.inf)
```

*about arguments*

Leaderboard:

| Average Total Reward | Method | Institution | Paper | Code |
|----------------------|--------|--------------|-------|------|
|  x                   | PPO    | UMD          |       |      |


### Waterworld

| Observations | Actions    | Agents | Manual Control |
|--------------|------------|--------|----------------|
|     Vector (viewable)   |   Either     | 3 (+/-)| No             |

`pettingzoo.sisl.waterworld`

*image*

By default there are 5 agents (purple), 5 food targets (green) and 10 poison targets (red). Each agent has 30 range-limited sensors, depicted by the black lines, to detect neighboring agents, food and poison targets, resulting in 212 long vector of computed values about the environment for the observation space. They have a continuous action space represented as a 2 element vector, which corresponds to left/right and up/down thrust. The agents each receive a reward of 10 when more than one agent captures food together (the food is not destroyed), a shaping reward of 0.01 for touching food, a reward of -1 for touching poison, and a small negative reward when two agents collide based on the force of the collision. The enviroment runs for 500 frames.

```
waterworld.env(n_pursuers=5, n_evaders=5, n_coop=2, n_poison=10, radius=0.015,
obstacle_radius=0.2, obstacle_loc=np.array([0.5, 0.5]), ev_speed=0.01,
poison_speed=0.01, n_sensors=30, sensor_range=0.2, action_scale=0.01,
poison_reward=-1., food_reward=10., encounter_reward=.01, control_penalty=-.5,
reward_mech='local', addid=True, speed_features=True)
```

*about arguments*

Leaderboard:

| Average Total Reward | Method | Institution | Paper | Code |
|----------------------|--------|--------------|-------|------|
|  x                   | PPO    | UMD          |       |      |

Add Gupta et al and DDPG paper results too


## Other Enviroments

`pettingzoo.other_envs`

| Environment             | Observations | Actions    | Agents | Manual Control |
|-------------------------|--------------|------------|--------|----------------|
| Rock Paper Scissors                | Vector            | Discrete |   2    | No             |
| Rock Paper Scissors Lizard Spock     |  Vector      | Discrete   | 2 | No             |

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
