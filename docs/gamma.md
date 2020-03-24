## Gamma Environments

| Environment             | Observations | Actions    | Agents  | Manual Control | Action Shape | Action Values | Observation Shape                     | Observation Values | Num States |
|-------------------------|--------------|------------|---------|----------------|--------------|-------------------|------------|-|-|
| Cooperative Pong        | Graphical    | Discrete   | 2       | Yes            | ?            | ?                 | ?          | ? | ? |
| Knights Archers Zombies | Graphical    | Discrete   | 4 (+/-) | Yes            | ?            | ?                 | ?          | ? | ? |
| Pistonball              | Graphical    | Either     | 20      | Yes            | ?            | ?                 | ?          | ? | ? |
| Prison                  | Either       | Either     | 8       | Yes            | ?            | ?                 | ?          | ? | ? |
| Prospector              | Graphical    | Continuous | 7 (+/-) | Yes            | ?            | ?                 | ?          | ? | ? |


`pip install pettingzoo[gamma]`

*General notes on environments*


### Cooperative Pong

| Observations | Actions  | Agents | Manual Control | Action Shape | Observation Shape | Num States |
|--------------|----------|--------|----------------|--------------|-------------------|------------|
| Graphical    | Discrete | 2      | Yes            | ?            | ?                 | ?          |

`from pettingzoo.gamma import cooperative_pong`

*gif*

*AEC diagram*

*blurb*

```
cooperative_pong.env(ball_velocity=?, left_paddle_velocity=?,
right_paddle_velocity=?, wedding_cake_paddle=True, max_frames=900)
```

*about arguments*

Leaderboard:

| Average Total Reward | Method | Institution | Paper | Code |
|----------------------|--------|-------------|-------|------|
| x                    | x      | x           | x     | x    |


### Knights Archers Zombies ('KAZ')

| Observations | Actions  | Agents  | Manual Control | Action Shape | Observation Shape | Num States |
|--------------|----------|---------|----------------|--------------|-------------------|------------|
| Graphical    | Discrete | 4 (+/-) | Yes            | ?            | ?                 | ?          |

`from pettingzoo.gamma import knights_archers_zombies`

*gif*

*AEC diagram*

Zombies walk from the top border of the screen down to the bottom border in unpredictable paths. The agents you control are knights and archers (default 2 knights and 2 archers) that are initially positioned at the bottom border of the screen. Each agent can rotate clockwise or counter-clockwise and move forward or backward. Each agent can also attack to kill zombies. When a knight attacks, it swings a mace in an arc in front of its current heading direction. When an archer attacks, it fires an arrow in a straight line in the direction of the archer's heading. The game ends when all agents die (collide with a zombie) or a zombie reaches the bottom screen border. An agent gets a reward when it kills a zombie. Each agent observes the environment as a square region around itself, with its own body in the center of the square. The observation is represented as a 1600-element vector (40x40 grid around the agent).

```
knights_archers_zombies.env(spawn_rate=?, knights=2, archers=2, 
killable_knights=True, killable_archers=True, line_death=True, max_frames=900)
```

*about arguments*

Leaderboard:

| Average Total Reward | Method | Institution | Paper | Code |
|----------------------|--------|-------------|-------|------|
| x                    | x      | x           | x     | x    |


### Pistonball

| Observations | Actions | Agents | Manual Control | Action Shape | Observation Shape | Num States |
|--------------|---------|--------|----------------|--------------|-------------------|------------|
| Graphical    | Either  | 20     | Yes            | ?            | ?                 | ?          |

`from pettingzoo.gamma import pistonball`

*gif*

*AEC diagram*

*blurb*

```
pistonball.env(local_ratio=.02, continuous=False, random_drop=True,
starting_angular_momentum=True, ball_mass = .75, ball.friction=.3,
ball.elasticity=1.5, max_frames=900)
```

*about arguments*

Discrete Leaderboard:

| Average Total Reward | Method | Institution | Paper | Code |
|----------------------|--------|-------------|-------|------|
| x                    | x      | x           | x     | x    |

Continuous Leaderboard:

| Average Total Reward | Method | Institution | Paper | Code |
|----------------------|--------|-------------|-------|------|
| x                    | x      | x           | x     | x    |


### Prison

| Observations | Actions | Agents | Manual Control | Action Shape | Observation Shape | Num States |
|--------------|---------|--------|----------------|-------------|------------------|------------|
| Either       | Either  | 8      | Yes            | ?           | ?                | ?          |


`from pettingzoo.gamma import prison`

*gif*

*blurb*

Arguments:
```
prison.env(graphical_output=True, discrete_input=True, syncronized_start=False,
max_frames=900)
```

*about arguments*

Discrete Leaderboard:

| Average Total Reward | Method | Institution | Paper | Code |
|----------------------|--------|-------------|-------|------|
| x                    | x      | x           | x     | x    |

Continuous Leaderboard:

| Average Total Reward | Method | Institution | Paper | Code |
|----------------------|--------|-------------|-------|------|
| x                    | x      | x           | x     | x    |


### Prospector

| Observations | Actions    | Agents  | Manual Control | Action Shape | Observation Shape | Num States |
|--------------|------------|---------|----------------|--------------|-------------------|------------|
| Graphical    | Continuous | 7 (+/-) | Yes            | ?            | ?                 | ?          |

`from pettingzoo.gamma import prospector`

*gif*

*AEC diagram*

This game is inspired by gold panning in the American "wild west" movies. There's a blue river at the bottom of the screen, which contains gold. 4 "panner" agents can move and touch the river and pan from it, and get a gold nugget (visibly held by them). They take a 3 element vector of continuous values (the first for forward/backward, the second for left/right movement, the third for clockwise/counter-clockwise rotation). They can only hold 1 nugget at a time.

There are a handful of bank chests at the top of the screen. The panner agents can hand their held gold nugget to the 2 "manager" agents, to get a reward. The manager agents can't rotate, and the panner agents must give the nuggets (which are held in the front of their body) to the front (always pointing upwards) of the managers. The managers then get the gold, and can deposit it into the chests to recieve a reward. They take a 2 element vector of continuous values (the first for forward/backward, the second for left/right movement). They can only hold 1 nugget at a time.

*arguments and about arguments*
(mention max_frames=900)

Leaderboard:

| Average Total Reward | Method | Institution | Paper | Code |
|----------------------|--------|-------------|-------|------|
| x                    | x      | x           | x     | x    |
