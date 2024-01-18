import os
import sys

from pettingzoo.utils import AECEnv, ParallelEnv

# Initializing pygame initializes audio connections through SDL. SDL uses alsa by default on all Linux systems
# SDL connecting to alsa frequently create these giant lists of warnings every time you import an environment using pygame
# DSP is far more benign (and should probably be the default in SDL anyways)

if sys.platform.startswith("linux"):
    os.environ["SDL_AUDIODRIVER"] = "dsp"

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

__version__ = "1.24.3"

try:
    import sys

    from farama_notifications import notifications

    if "pettingzoo" in notifications and __version__ in notifications["pettingzoo"]:
        print(notifications["pettingzoo"][__version__], file=sys.stderr)
except Exception:  # nosec
    pass
