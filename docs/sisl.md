---
layout: env_selection
title: SISL Environments
---
<div class="selection-content" markdown="1">

The unique dependencies for this set of environments can be installed via:

````bash
pip install pettingzoo[sisl]
````

The SISL environments are a set of three cooperative multi-agent benchmark environments, created at SISL (Stanford Intelligent Systems Laboratory)) and released as part of "Cooperative multi-agent control using deep reinforcement learning." The code was originally released at: https://github.com/sisl/MADRL

Please note that we've made major bug fixes to all environments included. As such, we discourage directly comparing results on these environments to those in the original paper.

If you use these environments, please additionally cite:

```
@inproceedings{gupta2017cooperative,
  title={Cooperative multi-agent control using deep reinforcement learning},
  author={Gupta, Jayesh K and Egorov, Maxim and Kochenderfer, Mykel},
  booktitle={International Conference on Autonomous Agents and Multiagent Systems},
  pages={66--83},
  year={2017},
  organization={Springer}
}
```

</div>
<div class="selection-table-container" markdown="1">
## SISL

{% include bigtable.html group="sisl/" cols=3 %}
</div>
