## Classic Environments


{% include bigtable.html group="classic/" %}

`pip install pettingzoo[classic]`

Classic environments represent implementations of popular turn based human games and are mostly competitive. The classic environments have a few differences from others in this library:

* No classic environments currently take any environment arguments
* All classic environments are rendered solely via printing to terminal
* Many classic environments have illegal moves in the action space, and describe legal moves in  `env.infos[agent]['legal_moves']`. In environments that use this, taking an illegal move will give a reward of -1 to the illegally moving player and 0 to the other players before ending the game. Note that this list is only well defined right before the agents takes its step.
* Reward for most environments only happens at the end of the games once an agent wins or losses, with a reward of 1 for winning and -1 for losing.

Many environments in classic are based on [RLCard](https://github.com/datamllab/rlcard). If you use these libraries in your research, please cite them:

```
@article{zha2019rlcard,
  title={RLCard: A Toolkit for Reinforcement Learning in Card Games},
  author={Zha, Daochen and Lai, Kwei-Herng and Cao, Yuanpu and Huang, Songyi and Wei, Ruzhe and Guo, Junyu and Hu, Xia},
  journal={arXiv preprint arXiv:1910.04376},
  year={2019}
}
```
