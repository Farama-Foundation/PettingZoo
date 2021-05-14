from pettingzoo.utils import AECEnv, ParallelEnv
import sys

# Initializing pygame initializes audio connections through SDL. SDL uses alsa by default on all Linux systems
# SDL connecting to alsa frequently create these giant lists of warnings every time you import an environment using pygame
# DSP is far more benign (and should probably be the default in SDL anyways)

if sys.platform.startswith('linux'):
    import os
    os.environ['SDL_AUDIODRIVER'] = 'dsp'


__version__ = "1.8.2"
