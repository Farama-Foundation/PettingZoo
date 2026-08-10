---
title: MAgent Environments
firstpage:
---

# MAgent (moved to MAgent2)

```{warning}
The MAgent environments are no longer part of PettingZoo. They now live in their own
Farama project, **[MAgent2](https://magent2.farama.org/)**, where they continue to be maintained.

Importing `pettingzoo.magent` raises an `ImportError` pointing here.
```

## Migration Guide

Install the new package:

````bash
pip install magent2
````

Then update your imports. The environment names and versions are unchanged, so in most
cases swapping the import is the only edit required:

```python notest
# Before (PettingZoo <= 1.23)
from pettingzoo.magent import battle_v4

# After
from magent2.environments import battle_v4

env = battle_v4.env(render_mode="human")
```

MAgent2 still implements the PettingZoo [AEC](/api/aec/) and [Parallel](/api/parallel/) APIs,
so the rest of your code, along with any PettingZoo wrappers and utilities, continues to work.

## Environments

The environments that used to be documented on this site are now documented at
[magent2.farama.org](https://magent2.farama.org/):

- [Adversarial Pursuit](https://magent2.farama.org/environments/adversarial_pursuit/)
- [Battle](https://magent2.farama.org/environments/battle/)
- [Battlefield](https://magent2.farama.org/environments/battlefield/)
- [Combined Arms](https://magent2.farama.org/environments/combined_arms/)
- [Gather](https://magent2.farama.org/environments/gather/)
- [Tiger Deer](https://magent2.farama.org/environments/tiger_deer/)

## Links

- Documentation: [https://magent2.farama.org/](https://magent2.farama.org/)
- GitHub: [https://github.com/Farama-Foundation/MAgent2](https://github.com/Farama-Foundation/MAgent2)
- PyPI: [https://pypi.org/project/magent2/](https://pypi.org/project/magent2/)
