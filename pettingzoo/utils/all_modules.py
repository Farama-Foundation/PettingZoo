from pettingzoo.atari.all_modules import atari_environments
from pettingzoo.butterfly.all_modules import butterfly_environments
from pettingzoo.classic.all_modules import classic_environments
from pettingzoo.mpe.all_modules import mpe_environments
from pettingzoo.sisl.all_modules import sisl_environments

all_prefixes = ["atari", "classic", "butterfly", "mpe", "sisl"]

# environments which have manual policy scripts, allowing interactive play
manual_environments = {
    "butterfly/knights_archers_zombies",
    "butterfly/pistonball",
    "butterfly/cooperative_pong",
    "sisl/pursuit",
}

all_environments = {
    **atari_environments,
    **butterfly_environments,
    **classic_environments,
    **mpe_environments,
    **sisl_environments,
}
