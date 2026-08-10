---
title: MPE Environments
firstpage:
---

# MPE (moved to MPE2)

```{warning}
The MPE environments are no longer part of PettingZoo. They now live in their own
Farama project, **[MPE2](https://mpe2.farama.org/)**, where they continue to be maintained.

Importing `pettingzoo.mpe` raises an `ImportError` pointing here.
```

## Migration Guide

Install the new package:

````bash
pip install mpe2
````

Then update your imports. The environment names and versions are unchanged, so in most
cases swapping the import is the only edit required:

```python notest
# Before (PettingZoo <= 1.24)
from pettingzoo.mpe import simple_spread_v3

# After
from mpe2 import simple_spread_v3

env = simple_spread_v3.env(render_mode="human")
```

MPE2 still implements the PettingZoo [AEC](/api/aec/) and [Parallel](/api/parallel/) APIs,
so the rest of your code, along with any PettingZoo wrappers and utilities, continues to work.

## Environments

The environments that used to be documented on this site are now documented at
[mpe2.farama.org](https://mpe2.farama.org/):

- [Simple](https://mpe2.farama.org/environments/simple/)
- [Simple Adversary](https://mpe2.farama.org/environments/simple_adversary/)
- [Simple Crypto](https://mpe2.farama.org/environments/simple_crypto/)
- [Simple Push](https://mpe2.farama.org/environments/simple_push/)
- [Simple Reference](https://mpe2.farama.org/environments/simple_reference/)
- [Simple Speaker Listener](https://mpe2.farama.org/environments/simple_speaker_listener/)
- [Simple Spread](https://mpe2.farama.org/environments/simple_spread/)
- [Simple Tag](https://mpe2.farama.org/environments/simple_tag/)
- [Simple World Comm](https://mpe2.farama.org/environments/simple_world_comm/)

MPE2 also adds environments that were never part of PettingZoo, including
[Simple Formation](https://mpe2.farama.org/environments/simple_formation/),
[Simple Line](https://mpe2.farama.org/environments/simple_line/), and
[Collect Treasure](https://mpe2.farama.org/environments/collect_treasure/).

## Links

- Documentation: [https://mpe2.farama.org/](https://mpe2.farama.org/)
- GitHub: [https://github.com/Farama-Foundation/MPE2](https://github.com/Farama-Foundation/MPE2)
- PyPI: [https://pypi.org/project/mpe2/](https://pypi.org/project/mpe2/)
