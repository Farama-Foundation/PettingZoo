## SISL Enviroments

| Environment | Observations      | Actions  | Agents  | Manual Control | Action Shape | Action Values | Observation Shape                     | Observation Values | Num States |
|-------------|-------------------|----------|---------|----------------|--------------|---------------|---------------------------------------|--------------------|------------|
| Multiwalker | Vector (viewable) | Discrete | 3 (+/-) | No             | (4)          | (-1, 1)       | (31)                                  | (-5.3, 5.3)        | ?          |
| Pursuit     | Graphical         | Either   | 8 (+/-) | No             | (1,)         | Discrete(5)   | (3, obs_range, obs_range)             | (0,255)            | xs*ys      |
| Waterworld  | Vector (viewable) | Either   | 3 (+/-) | No             | (2,)         | (-1, 1)       | ((4 + 3*speed_features)*n_sensors+2,) | (-10,10)           | ?          |


`pip install pettingzoo[sisl]`

*General notes on environments*

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

### Multiwalker

| Observations | Actions  | Agents  | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|--------------|----------|---------|----------------|--------------|---------------|-------------------|--------------------|------------|
| Vector       | Discrete | 3 (+/-) | No             | (4)          | (-1, 1)       | (31)              | (-5.3, 5.3)        | ?          |




`from pettingzoo.sisl import multiwalker`

*gif*

*AEC diagram*

A package is placed on top of (by default) 3 pairs of robot legs which you control. The robots must learn to move the package as far as possible to the right. Each walker gets a reward of 1 for moving the package forward, and a reward of -100 for dropping the package. Each walker exerts force on two joints in their two legs, giving a continuous action space represented as a 4 element vector. Each walker observes via a 32 element vector, containing simulated noisy lidar data about the environment and information about neighboring walkers. The environment runs for 500 frames by default.

```
multiwalker.env(n_walkers=3, position_noise=1e-3, angle_noise=1e-3, reward_mech='local',
forward_reward=1.0, fall_reward=-100.0, drop_reward=-100.0, terminate_on_fall=True,
max_frames=500)
```

*about arguments*

```
n_walkers: number of bipedal walker agents in environment

position_noise: noise applied to agent positional sensor observations

angle_noise: noise applied to agent rotational sensor observations

reward_mech: whether all agents are rewarded equal amounts or singular agent is rewarded

forward_reward: reward applied for an agent standing, scaled by agent's x coordinate

fall_reward: reward applied when an agent falls down

drop_reward: reward applied for each fallen walker in environment

terminate_on_fall: toggles whether agent is done if it falls down

max_frames: after max_frames steps all agents will return done

```

Leaderboard:

| Average Total Reward | Method | Institution | Paper | Code |
|----------------------|--------|-------------|-------|------|
| x                    | PPO    | UMD         |       |      |

Add Gupta et al and DDPG paper results too

### Pursuit

| Observations | Actions | Agents  | Manual Control | Action Shape | Action Values | Observation Shape         | Observation Values | Num States |
|--------------|---------|---------|----------------|--------------|---------------|---------------------------|--------------------|------------|
| Graphical    | Either  | 8 (+/-) | No             | (1,)         | Discrete(5)   | (3, obs_range, obs_range) | (0,255)            | xs*ys      |


`from pettingzoo.sisl import pursuit`

*gif*

*AEC diagram*

By default there are 30 blue evaders and 8 red pursuer agents, in a 16 x 16 grid with an obstacle in the center, shown in white. The evaders move randomly, and the pursuers are controlled. Every time the pursuers fully surround an evader, each of the surrounding agents receives a reward of 5, and the evader is removed from the environment. Pursuers also receive a reward of 0.01 every time they touch an evader. The pursuers have a discrete action space of up, down, left, right and stay. Each pursuer observes a 7 x 7 grid centered around itself, depicted by the orange boxes surrounding the red pursuer agents. The enviroment runs for 500 frames by default.

```
pursuit.env(max_frames=500, xs=16, ys=16, reward_mech='local', n_evaders=30, n_pursuers=8,
obs_range=7, layer_norm=10, n_catch=2, random_opponents=False, max_opponents=10,
freeze_evaders=False, catchr=0.01, caughtr=-0.01, term_pursuit=5.0,
urgency_reward=0.0, surround=True, constraint_window=1.0,
train_pursuit=True, ally_layer=AgentLayer(xs, ys, n_pursuers),
opponent_layer=AgentLayer(xs, ys, n_evaders))

```

*about arguments*
```
max_frames: after max_frames steps all agents will return done

xs, ys: size of environment world space

reward_mech: Whether a single pursuer is rewarded for an evader being caught, or all pursuers are rewarded

n_evaders: Number of evaders

n_pursuers: Number of pursuers

obs_range: Radius of agent observation view

n_catch: Number pursuers required around an evader to be considered caught

random_opponents: Whether to randomize number of evaders on reset or use argument amount

max_opponents: Maximum number of random evaders on reset, if random_opponents specified

freeze_evaders: Toggles if evaders can move or not

catchr: Reward for 'tagging' a single evader

caughtr: Reward for getting 'tagged' by a pursuer

term_pursuit: Reward added when a pursuer or pursuers catch an evader

urgency_reward: Reward to agent added in each step

surround: Toggles whether evader is removed when surrounded, or when n_catch pursuers are on top of evader

constraint_window: Window in which agents can randomly spawn into the environment world

train_pursuit: Flag indicating if we are simulating pursuers or evaders

ally_layer: Initial pursuers in world

opponent_layer: Initial evader in world
```

Leaderboard:

| Average Total Reward | Method | Institution | Paper | Code |
|----------------------|--------|-------------|-------|------|
| x                    | PPO    | UMD         |       |      |

### Waterworld

| Observations      | Actions | Agents  | Manual Control | Action Shape | Action Values | Observation Shape                     | Observation Values | Num States |
|-------------------|---------|---------|----------------|--------------|---------------|---------------------------------------|--------------------|------------|
| Vector (viewable) | Either  | 3 (+/-) | No             | (2,)         | (-1, 1)       | ((4 + 3*speed_features)*n_sensors+2,) | (-10,10)           | ?          |

`from pettingzoo.sisl import waterworld`

*gif*

*AEC diagram*

By default there are 5 agents (purple), 5 food targets (green) and 10 poison targets (red). Each agent has 30 range-limited sensors, depicted by the black lines, to detect neighboring agents, food and poison targets, resulting in 212 long vector of computed values about the environment for the observation space. They have a continuous action space represented as a 2 element vector, which corresponds to left/right and up/down thrust. The agents each receive a reward of 10 when more than one agent captures food together (the food is not destroyed), a shaping reward of 0.01 for touching food, a reward of -1 for touching poison, and a small negative reward when two agents collide based on the force of the collision. The enviroment runs for 500 frames by default.

```
waterworld.env(n_pursuers=5, n_evaders=5, n_coop=2, n_poison=10, radius=0.015,
obstacle_radius=0.2, obstacle_loc=np.array([0.5, 0.5]), ev_speed=0.01,
poison_speed=0.01, n_sensors=30, sensor_range=0.2, action_scale=0.01,
poison_reward=-1., food_reward=10., encounter_reward=.01, control_penalty=-.5,
reward_mech='local', speed_features=True, max_frames=500)
```

*about arguments*

```
n_pursuers: number of pursuing archea

n_evaders: number of evaders

n_coop: how many archea touching food at same time for food to be considered consumed

n_poison: number of poison objects

radius: pursuer archea radius

obstacle_radius: radius of obstacle object

obstacle_loc: coordinate of obstacle object

ev_speed: evading archea speed

poison_speed: speed of poison object

n_sensors: number of sensor dendrites on all archea

sensor_range: length of sensor dendrite on all archea

action_scale: scaling factor applied to all input actions

poison_reward: reward for pursuer consuming a poison object

food_reward: reward for pursuers consuming an evading archea

encounter_reward: reward for a pursuer colliding with another archea

control_penalty: reward added to pursuer in each step

reward_mech: controls whether all pursuers are rewarded equally or individually

speed_features: toggles whether archea sensors detect speed of other objects

max_frames: after max_frames steps all agents will return done

```

Leaderboard:

| Average Total Reward | Method | Institution | Paper | Code |
|----------------------|--------|-------------|-------|------|
| x                    | PPO    | UMD         |       |      |

Add Gupta et al and DDPG paper results too
