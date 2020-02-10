# Zombie Shooter

A Zombie Shooting/Killing Game with two players-

Archer (Red) - Shoots an arrow

Knight (Blue) - Swings a mace

## Prerequisites

Run the following command to install the dependencies

```sudo pip3 install -r requirements.txt```

## Playing

```python3 game.py```

### Archer

Move the archer using the 'W', 'A', 'S' and 'D' keys. Shoot the Arrow using 'F' key. Rotate the archer using 'Q' and 'E' keys.
Press 'X' key to spawn a new archer.

### Knight

Move the knight using the 'I', 'J', 'K' and 'L' keys. Stab the Sword using ';' key. Rotate the knight using 'U' and 'O' keys.
Press 'M' key to spawn a new knight.

## Known Bugs
    - When a knight is created and it spawns the sword, the second knight if spawned thereafter cannot spawn its sword unless the sword of the first knight kills a zombie or comes back in (whichever is first). So, the second knight has to wait for that small duration.

    - Downscaling the observation and saving it as an image with skimage.io.imsave results in an all-black image. Throws a "low constrast" warning, too. 