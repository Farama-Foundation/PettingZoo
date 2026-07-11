from pettingzoo.atari.all_modules import atari_environments
from pettingzoo.butterfly.all_modules import butterfly_environments
from pettingzoo.classic.all_modules import classic_environments
from pettingzoo.env_registry.registration import aec_registry, parallel_registry
from pettingzoo.env_registry.spec import _normalize_env_id
from pettingzoo.sisl.all_modules import sisl_environments

all_prefixes = ["atari", "classic", "butterfly", "sisl"]

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
    **sisl_environments,
}

# Verify that every env declared in all_modules is registered
_declared_ids = {_normalize_env_id(env_id) for env_id in all_environments}
_missing_aec = _declared_ids - set(aec_registry.keys())
_missing_parallel = _declared_ids - set(parallel_registry.keys())
assert not _missing_aec, (
    f"Environments missing from AEC registry: {sorted(_missing_aec)}"
)
assert not _missing_parallel, (
    f"Environments missing from Parallel registry: {sorted(_missing_parallel)}"
)
