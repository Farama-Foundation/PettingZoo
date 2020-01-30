# TODO

1. When a knight is created and it spawns the sword, the second knight if spawned thereafter cannot spawn its sword unless
the sword of the first knight kills a zombie or comes back in (whichever is first). So, the second knight has to wait for
that small duration.


===


Note bug 1 exists (future work)

Sprites

API

Folder name


===================================

-Can the arrow sprite be rotated so that they're pointing in the direction of travel?

-Can the archer sprites be of an archer dude or elf or something and not just a cross bow?

-We need some sort of background. We can't have a full pixel art background for performance reasons. Can we like, get castle walls or something on the edges and something that can pass for a decent floor with pygame.draw for the rest?

-I assume this is disabled for testing purposes, but the game needs to stop after 900 frames (60 seconds at 15 fps) and when a zombie crosses the bottom of the screeen

-Sometimes the arrows dont kill the zombies on contact

-How does hit detection work with the sprites that aren't regular shapes?

-Alternative floor solution: Use a sprite floor, display it tiled, and only redraw it when something moves near it so you aren't redrawing most of the screen

-The arrows actually dont kill the zombies on contact a lot

-The game shouldn't print things, aside from debugging purposes (i.e. no 'game over' print out)
