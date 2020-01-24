# TODO

1. When a knight is created and it spawns the sword, the second knight if spawned thereafter cannot spawn its sword unless
the sword of the first knight kills a zombie or comes back in (whichever is first). So, the second knight has to wait for
that small duration.

2. As of now, when the knight dies, its sword doesn't die and it remains until it touched a zombie or comes back in (whichever
is first). 

- (According to me, both the above problems don't seem very concerning because of the sword's ability to stab and go back in.
Hence, I feel it might not be a very big issue. However, I understand that not fixing it makes it vulnerable for the agents
to learn incorrect policies.)

3. Rotating the sword when the knight rotates with respect to the knight's center. As per my discussion with Ananth, the most feasible solution to this was to first rotate the knight, rotate the sword by the same angle and then translate the bottom edge of the sword's rect to the top edge of the knight's rect. I tried that, but it jumps around a lot as the knight rotates. 
I have the commented code for that. Maybe I am not calculating it the way I should.

The other solution was to spawn a new sword at every instance of its rotation. However, that made things more difficult since I needed the coordinates when the sword was inclined at an angle.

4. Create a reset() and step() function and use the ray.rllib library.

5. For the main while loop, I could change the keypress to pygame.event.key. However, for the players and weapons classes, 
I couldn't implement that since somehow, the event didn't respond when it was carried forward inside those classes. So, I have
kept keypress for those right now.

6. Ananth suggested me to append new objects to the sprite list instead of a dictionary to make things easier. However, that 
didn't work out for some unknown reasons. And actually using a dictionary is making things very difficult especially for cases
like points 1 & 2.

====

change the sword to a mace and make it swing around the knight.
    - pause knight movement during mace swing

fix bugs 1 and 2

api

sprite