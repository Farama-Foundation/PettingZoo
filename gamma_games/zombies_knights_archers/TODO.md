# TODO

1. When a knight is created and it spawns the sword, the second knight if spawned thereafter cannot spawn its sword unless
the sword of the first knight kills a zombie or comes back in (whichever is first). So, the second knight has to wait for
that small duration.


===

Note bug 1 exists (future work)

API

-We need some sort of background. We can't have a full pixel art background for performance reasons. Can we like, get castle walls or something on the edges and something that can pass for a decent floor with pygame.draw for the rest?
    -Alternative floor solution: Use a sprite floor, display it tiled, and only redraw it when something moves near it so you aren't redrawing most of the screen

-How does hit detection work with the sprites that aren't regular shapes?

-Step and reset need to return the dicts returned in pistonball/cooperative pong
    most of it's trivial (give a reward of 5 for killing a zombie, done, etc.)
    observe is more interesting
    the observation for each agent should be a certain box around them, returning black if it's outside the screen
    maybe like 8 agents x 8 agents in size?
    Look at the observe function in pistonball to see how
