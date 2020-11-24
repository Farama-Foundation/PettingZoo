import sys
import json
from .all_modules import all_environments
from .seed_test import calc_hash, seed_action_spaces


def gen_hashes():
    out_hashes = {}
    for name, module in (all_environments.items()):
        try:
            env = module.env(max_cycles=20)
        except TypeError:
            env = module.env()

        base_seed = 42
        env.seed(base_seed)
        seed_action_spaces(env)
        out_hashes[name] = calc_hash(env, 0, 50)
    return out_hashes


if __name__ == "__main__":
    assert len(sys.argv) == 2, "needs argument <out_hashes_filename>"
    out = json.dumps(gen_hashes(), indent=2, sort_keys=True)
    with open(sys.argv[1], 'w') as file:
        file.write(out)
