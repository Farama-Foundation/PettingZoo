## Butterfly Environments


{% include bigtable.md group="butterfly" %}

`pip install pettingzoo[butterfly]`

All butterfly environments were created by us using PyGame with visual Atari spaces. In Prison, all agents are completely independent (i.e. no coordination is possible, each agent is in it's own cell) It is intended as a debugging tool.

All other environments require a high degree of coordination and learning emergent behaviors to achieve an optimal policy. As such, these environments are currently very challenging to learn.

All environments are highly configurable with environment arguments.
