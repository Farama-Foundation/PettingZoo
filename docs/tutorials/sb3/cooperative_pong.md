---
title: "Cooperative Pong: a scripted policy for the documentation GIF"
---

# Cooperative Pong: a scripted policy for the documentation GIF

This page documents the policy behind the [Cooperative Pong](/environments/butterfly/cooperative_pong/) GIF. It is a hand-written rule, not a trained model: each paddle finds the ball in the rendered frame and moves toward its row.

```{figure} cooperative_pong_policy.gif
    :alt: Two paddles rallying the ball for a full episode
    :width: 480
```

```{eval-rst}
.. note::

    Nothing here is learned. The environment is simple enough that a few lines of pixel arithmetic keep the ball in play indefinitely, which makes it a cheap and fully reproducible source for a documentation GIF.
```

## How the policy sees the field

The observation is the whole screen, and every entity renders in the same white, so the ball cannot be found by colour. It is separated by *position* instead. Measured on a `280x480` frame:

| entity | columns |
| --- | --- |
| left paddle | 0–9 |
| ball | a ~10px-wide run between the paddles |
| right paddle (the wider "cake" paddle) | four stacked rectangles spanning 420–479 |

Both paddles are anchored to their own screen edge and the ball never is, so the detector takes the lit run reaching each edge as that paddle and whatever is lit in between as the ball. One detector serves both agents with no per-agent tuning.

Cutting fixed columns instead would be simpler but wrong: the right paddle is 60px of staircase, and a cut wide enough to contain it also hides any ball in that strip. Checked against the environment's own rectangles over 18,000 frames, this detector never misreads the ball except on the frames where it is touching a paddle, by which point the bounce is already decided.

A deadzone stops a paddle oscillating around a ball it is already lined up with. Without it the paddle jitters and loses ground when the ball approaches steeply.

## Results

Both paddles use the same rule. Reward is per paddle, and a full episode is `max_cycles=900`.

| seeds | policy reward | policy steps | full-length | random reward | random steps |
| --- | --- | --- | --- | --- | --- |
| 0–49 | **100.00 ± 0.00** | 900.0 | 50/50 | −3.31 ± 5.98 | 61.2 |
| 1000–1049 | **100.00 ± 0.00** | 900.0 | 50/50 | −2.56 ± 8.39 | 67.9 |

The second block is disjoint from the first and gives an identical result, so the policy is not tuned to a particular seed. The seeded random control never completes an episode; it drops the ball after about 60 steps.

The script binds `cooperative_pong_v7` if it is present and falls back to `v6`, so it keeps working across the rename in #1398. That fallback is tested, not assumed: applying #1398 locally and rerunning both seed blocks gives the same 100.00 ± 0.00, 50/50.

## Environment Setup

```{eval-rst}
.. literalinclude:: ../../../tutorials/SB3/cooperative_pong/requirements.txt
   :language: text
```

## Reproducing

```bash
# the table above
python tutorials/SB3/cooperative_pong/cooperative_pong_policy.py --episodes 50
python tutorials/SB3/cooperative_pong/cooperative_pong_policy.py --episodes 50 --seed-start 1000

# the GIF on this page
python tutorials/SB3/cooperative_pong/cooperative_pong_policy.py \
    --gif docs/tutorials/sb3/cooperative_pong_policy.gif --gif-seed 1
```

The script prints the seeded random control alongside the policy on every run, so a degenerate result stays visible rather than being quietly flattering.

## Code

```{eval-rst}
.. literalinclude:: ../../../tutorials/SB3/cooperative_pong/cooperative_pong_policy.py
   :language: python
```
