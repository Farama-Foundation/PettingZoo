from pettingzoo.atari import atari_environments
from pettingzoo.butterfly import butterfly_environments
from pettingzoo.classic import classic_environments
from pettingzoo.mpe import mpe_environments
from pettingzoo.sisl import sisl_environments

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
