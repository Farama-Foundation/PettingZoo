---
title: "Simple Crypto"
env_icon: "/_static/img/icons/MPE/SimpleCrypto.png"
---

# Simple Crypto

```{figure} mpe_simple_crypto.gif 
:width: 140px
:name: simple_crypto
```

This environment is part of the <a href='..'>MPE environments</a>. Please read that page first for general information.

| Import             | `from pettingzoo.mpe import simple_crypto_v2` |
|--------------------|-----------------------------------------------|
| Actions            | Discrete/Continuous                           |
| Parallel API       | Yes                                           |
| Manual Control     | No                                            |
| Agents             | `agents= [eve_0, bob_0, alice_0]`             |
| Agents             | 2                                             |
| Action Shape       | (4)                                           |
| Action Values      | Discrete(4)/Box(0.0, 1.0, (4))                |
| Observation Shape  | (4),(8)                                       |
| Observation Values | (-inf,inf)                                    |
| State Shape        | (20,)                                         |
| State Values       | (-inf,inf)                                    |

```{figure} ../../_static/img/aec/mpe_simple_crypto_aec.svg
:width: 200px
:name: simple_crypto
```

In this environment, there are 2 good agents (Alice and Bob) and 1 adversary (Eve). Alice must sent a private 1 bit message to Bob over a public channel. Alice and Bob are rewarded +2 if Bob reconstructs the message, but are rewarded -2 if Eve reconstruct the message (that adds to 0 if both teams reconstruct the bit). Eve is rewarded -2 based if it cannot reconstruct the signal, zero if it can. Alice and Bob have a private key (randomly generated at beginning of each episode) which they must learn to use to encrypt the message.


Alice observation space: `[message, private_key]`

Bob observation space: `[private_key, alices_comm]`

Eve observation space: `[alices_comm]`

Alice action space: `[say_0, say_1, say_2, say_3]`

Bob action space: `[say_0, say_1, say_2, say_3]`

Eve action space: `[say_0, say_1, say_2, say_3]`

For Bob and Eve, their communication is checked to be the 1 bit of information that Alice is trying to convey.

### Arguments

``` python
simple_crypto_v2.env(max_cycles=25, continuous_actions=False)
```



`max_cycles`:  number of frames (a step for each agent) until game terminates

`continuous_actions`: Whether agent action spaces are discrete(default) or continuous
