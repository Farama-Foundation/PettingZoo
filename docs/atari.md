## Atari Environments



{% include bigtable.html group="atari/" cols=4 %}

The Atari environments are based off the [Arcade Learning Environment](https://github.com/mgbellemare/Arcade-Learning-Environment). This environment was instrumental in the development of modern reinforcement learning, and so we hope that our [multi-agent version](https://github.com/PettingZoo-Team/Multi-Agent-ALE) of it will be useful in the development of multi-agent reinforcement learning.

### Games Overview

Most games have two players, with the exception of Warlords and a couple of Pong variations which have four players.

### Environment Details

The ALE has been studied extensively and a few notable problems have been identified:

* **Determinism**: The Atari console is deterministic, and so agents can theoretically memorize precise sequences of actions that will maximize the end score. This is not ideal, so we encourage the use of [SuperSuit's](https://github.com/PettingZoo-Team/SuperSuit) `sticky_actions` wrapper (example below). This is the recommended approach of  *"Machado et al. (2018), "Revisiting the Arcade Learning Environment: Evaluation Protocols and Open Problems for General Agents"*
* **Frame flickering**: Atari games often do not render every sprite every frame due to hardware restrictions. Instead, sprites (such as the knights in Joust) are sometimes rendered every other frame or even (in Wizard of Wor) every 3 frames. The standard way of handling this is a frame stack of the previous 4 observations (see example below for implementation).

### Preprocessing

We encourage the use of the [supersuit](https://github.com/PettingZoo-Team/SuperSuit) library for preprocessing. The unique dependencies for this set of environments can be installed via:

 ````bash
pip install supersuit
 ````

Here is some example usage for the Atari preprocessing:

```python
from supersuit import resize, frame_skip, frame_stack, sticky_actions
from pettingzoo.atari import space_invaders_v1

env = space_invaders_v1.env()

# repeat_action_probability is set to 0.25 to introduce non-determinism to the system
env = sticky_actions(env, repeat_action_probability=0.25)

# downscale observation for faster processing
env = resize(env, (84, 84))

# allow agent to see everything on the screen despite Atari's flickering screen problem
env = frame_stack(env, 4)

# skip frames for faster processing and less control
# to be compatable with gym, use frame_skip(env, (2,5))
env = frame_skip(env, 4)
```

### Common Parameters

All the Atari environments have the following environment parameters:

```python
<atari_game>.env(obs_type='rgb_image', full_action_space=True, max_cycles=100000, auto_rom_install_path=None)
```

`obs_type`:  There are three possible values for this parameter:

* 'rgb_image' (default) - produces an RGB image like you would see as a human player.
* 'grayscale_image' - produces a grayscale image.
* 'ram' - produces an observation of the 1024 bits that comprise the RAM of the Atari console.

`full_action_space`:  the effective action space of the Atari games is often smaller than the full space of 18 moves. Setting this to `False` shrinks the available action space to that smaller space.

`max_cycles`:  the number of frames (the number of steps that each agent can take) until game terminates.

`auto_rom_install_path`: The path to your AutoROM installation, installed
with the [PettingZoo-Team/AutoROM](https://github.com/PettingZoo-Team/AutoROM) tool.
This is the path you specified when installing AutoROM. For example, if
you're using the boxing Atari environment, then the library will look for
the rom at
`/auto_rom_install_path/ROM/boxing/boxing.bin`.
If this is not specified (has value `None`), then the library looks for roms
installed at the default AutoROM path.


### Citation

Multiplayer games within the Arcade Learning Environment were introduced in:

```
@article{terry2020arcade,
  Title = {Multiplayer Support for the Arcade Learning Environment},
  Author = {Terry, Justin K and Black, Benjamin},
  journal={arXiv preprint arXiv:2009.09341},
  year={2020}
}
```

The Arcade Learning Environment was originally introduced in:

```
@Article{bellemare13arcade,
  author = { {Bellemare}, M.~G. and {Naddaf}, Y. and {Veness}, J. and {Bowling}, M.},
  title = {The Arcade Learning Environment: An Evaluation Platform for General Agents},
  journal = {Journal of Artificial Intelligence Research},
  year = "2013",
  month = "jun",
  volume = "47",
  pages = "253--279",
}
```

Various extensions to the Arcade Learning Environment were introduced in:

```
@article{machado2018revisiting,
  title={Revisiting the arcade learning environment: Evaluation protocols and open problems for general agents},
  author={Machado, Marlos C and Bellemare, Marc G and Talvitie, Erik and Veness, Joel and Hausknecht, Matthew and Bowling, Michael},
  journal={Journal of Artificial Intelligence Research},
  volume={61},
  pages={523--562},
  year={2018}
}
```
