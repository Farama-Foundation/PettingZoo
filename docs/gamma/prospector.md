
### Prospector

This environment is part of the [gamma environments](../gamma.md). Please read that page first for general information.

| Actions    | Agents  | Manual Control | Action Shape | Action Values | Observation Shape | Observation Values | Num States |
|------------|---------|----------------|--------------|---------------|-------------------|--------------------|------------|
| Continuous | 7 (+/-) | Yes            | ?            | ?             | ?                 | ?                  | ?          |

`from pettingzoo.gamma import prospector_v0`

`agents= `

*gif*

*AEC diagram*

This game is inspired by gold panning in the American "wild west" movies. There's a blue river at the bottom of the screen, which contains gold. 4 "panner" agents can move and touch the river and pan from it, and get a gold nugget (visibly held by them). They take a 3 element vector of continuous values (the first for forward/backward, the second for left/right movement, the third for clockwise/counter-clockwise rotation). They can only hold 1 nugget at a time.

There are a handful of bank chests at the top of the screen. The panner agents can hand their held gold nugget to the 2 "manager" agents, to get a reward. The manager agents can't rotate, and the panner agents must give the nuggets (which are held in the front of their body) to the front (always pointing upwards) of the managers. The managers then get the gold, and can deposit it into the chests to recieve a reward. They take a 2 element vector of continuous values (the first for forward/backward, the second for left/right movement). They can only hold 1 nugget at a time. The game lasts for 900 frames by default.

*arguments*

*about arguments*

Leaderboard:

| Average Total Reward | Method | Institution | Paper | Code |
|----------------------|--------|-------------|-------|------|
| x                    | x      | x           | x     | x    |
