---
title: Migrating from SuperSuit
---

# Migrating from SuperSuit

[SuperSuit](https://github.com/Farama-Foundation/SuperSuit) has preprocessing wrappers for Gymnasium, PettingZoo AEC, and PettingZoo Parallel environments. PettingZoo is migrating multi-agent wrappers into its own package (see [#1365](https://github.com/Farama-Foundation/PettingZoo/issues/1365)). This initial inventory supports [#1481](https://github.com/Farama-Foundation/PettingZoo/issues/1481): it lists exported SuperSuit APIs, candidate destinations, and outstanding decisions.

**Important:** "Native" means the corresponding class exists in the inspected PettingZoo source, **not** that every old argument, supported space, edge case, or release has been tested for parity. At the time of this inventory, native classes are exposed through `pettingzoo.utils.wrappers`; the shorter `pettingzoo.wrappers` import path is separately tracked in [#1478](https://github.com/Farama-Foundation/PettingZoo/issues/1478). Check installed package versions before changing imports.

## Generic environment transformations

| SuperSuit API | PettingZoo destination | Migration note |
| --- | --- | --- |
| `clip_reward_v0` | `ClipRewardV1`, `ClipRewardParallelV1` | Native; parameters `min_reward` / `max_reward` replace `lower_bound` / `upper_bound` |
| `clip_actions_v0` | `ClipOutOfBoundsWrapper` (AEC and Parallel) | Native; warns on clipping and rejects NaNs; see [PR #1489](https://github.com/Farama-Foundation/PettingZoo/pull/1489) |
| `color_reduction_v0` | `ColorReductionObservationV1`, `ColorReductionObservationParallelV1` | Native; verify image layout and mode |
| `dtype_v0` | `DtypeObservationV1`, `DtypeObservationParallelV1` | Native; verify dtype behavior |
| `flatten_v0` | **Pending —** No identified native AEC/Parallel wrapper | Pending; Gymnasium FlattenObservation applies to Gymnasium environments, not directly to PettingZoo |
| `normalize_obs_v0` | `RescaleObservationV1`, `RescaleObservationParallelV1` | Native; new arguments `min_obs` / `max_obs`; finite float Box bounds required |
| `reshape_v0` | `ReshapeObservationV1`, `ReshapeObservationParallelV1` | Native; Box observation constraints apply |
| `resize_v1` | **Pending —** No identified native AEC/Parallel wrapper | Pending under [#1471](https://github.com/Farama-Foundation/PettingZoo/issues/1471) |
| `scale_actions_v0` | `ScaleActionV1`, `ScaleActionParallelV1` | Native; check scale and bounds semantics |
| `delay_observations_v0` | **Pending —** No identified native AEC/Parallel wrapper | Pending; needs narrow follow-up or maintainer decision |
| `frame_skip_v0` | `FrameSkipV1`, `FrameSkipParallelV1` | Native; check repeated steps and dynamic agents; [#1469](https://github.com/Farama-Foundation/PettingZoo/issues/1469) |
| `frame_stack_v1` | `FrameStackV3` (dispatches by environment API) | Native; verify `stack_dim` and initial padding; [#1470](https://github.com/Farama-Foundation/PettingZoo/issues/1470) |
| `frame_stack_v2` | `FrameStackV3 (dispatches by environment API)` | Native; verify differences in initialization and `stack_dim`; exported by SuperSuit through wildcard |
| `max_observation_v0` | `MaxObservationV1`, `MaxObservationParallelV1` | Native; check per-agent history and supported spaces |
| `nan_noop_v0` | `NanNoopV1`, `NanNoopParallelV1` | Native; check no-op configuration |
| `nan_random_v0` | `NanRandomV1`, `NanRandomParallelV1` | Native; check mask handling |
| `nan_zeros_v0` | `NanZerosV1`, `NanZerosParallelV1` | Native; check action-space restrictions |
| `sticky_actions_v0` | `StickyActionV1`, `StickyActionParallelV1` | Native; check reset and seeding behavior |

## Multi-agent-only transformations

| SuperSuit API | PettingZoo destination | Migration note |
| --- | --- | --- |
| `agent_indicator_v0` | `AgentIndicatorV1`, `AgentIndicatorParallelV1` | Native; verify `type_only` and observation shape |
| `black_death_v3` | `BlackDeathParallelV4` | Native for Parallel; semantics of departed agents and termination flags differ, not an AEC replacement |
| `pad_action_space_v0` | `PadActionSpaceV1`, `PadActionSpaceParallelV1` | Native; check padding for heterogeneous agents |
| `pad_observations_v0` | `PadObservationsV1`, `PadObservationsParallelV1` | Native; check observation-space support |

## Generic lambda wrappers: outstanding design decisions

SuperSuit publicly exports these three functions, but the older SuperSuit wrapper reference does not list them. The Gymnasium names below are **single-agent alternatives**, not direct AEC/Parallel replacements.

| SuperSuit API | Single-agent direction | AEC / Parallel status |
| --- | --- | --- |
| `observation_lambda_v0` | `gymnasium.wrappers.TransformObservation` | No verified general-purpose AEC/Parallel equivalent; custom wrapper or narrowly scoped issue requires maintainer decision |
| `action_lambda_v1` | `gymnasium.wrappers.TransformAction` | No verified general-purpose AEC/Parallel equivalent; multi-agent action and space transforms need design decision |
| `reward_lambda_v0` | `gymnasium.wrappers.TransformReward` | No verified general-purpose AEC/Parallel equivalent; AEC reward accumulation needs explicit treatment |

PettingZoo users can write specialized wrappers using `BaseWrapper` and `BaseParallelWrapper`, but that is not a complete compatibility policy for arbitrary functions of observation, action, reward, space, or agent. Maintainers should decide whether to document a custom-wrapper recipe or track a focused implementation for each missing multi-agent use case. Do not add placeholder public APIs just to preserve an old name.

## Vectorization and training adapters (separate workflow)

These six SuperSuit public APIs handle environment vectorization or integration with training libraries. They are **not** ordinary AEC/Parallel observation/action/reward wrappers. Replacement work belongs to [#1480](https://github.com/Farama-Foundation/PettingZoo/issues/1480), and must be completed or explicitly discontinued before retirement.

| SuperSuit API | Disposition / current verification |
| --- | --- |
| `vectorize_aec_env_v0` | AEC vectorization; replacement unverified |
| `pettingzoo_env_to_vec_env_v1` | PettingZoo Parallel-to-vector conversion; replacement unverified |
| `concat_vec_envs_v1` | Vector concatenation; replacement unverified |
| `gym_vec_env_v0` | Investigate gymnasium.vector for single-agent Gymnasium envs; parity unverified |
| `stable_baselines3_vec_env_v0` | Investigate maintained Stable-Baselines3 vector interfaces; parity unverified |
| `stable_baselines_vec_env_v0` | Legacy Stable-Baselines adapter; continued support needs maintainer decision |

## Single-agent Gymnasium use cases

SuperSuit could also wrap a `gymnasium.Env`. PettingZoo AEC/Parallel wrappers are **not valid drop-in replacements** for single-agent Gymnasium environments. For those users, inspect the [Gymnasium wrapper API](https://gymnasium.farama.org/api/wrappers/), including `FlattenObservation`, `ResizeObservation`, `TransformObservation`, `TransformAction`, and `TransformReward`. This is guidance on where to look, **not a validated one-to-one migration**: argument semantics, supported spaces, and the environment protocol must still be checked. Unsupported old behaviors require an explicit maintainer decision rather than an assumed replacement.

## Decisions required before declaring SuperSuit fully replaceable

1. Decide how to cover `flatten_v0` and `delay_observations_v0` for AEC/Parallel, creating narrow implementation issues if supported use cases lack a destination.
2. Complete [#1471](https://github.com/Farama-Foundation/PettingZoo/issues/1471) for native multi-agent image resizing and update this inventory.
3. Resolve the three generic lambda functions: native equivalents, documented custom-wrapper recipes, or explicit discontinuation decisions, including agent-specific functions and space transforms.
4. Verify the single-agent Gymnasium migration matrix, recording which old behaviors are no longer supported.
5. Resolve the six vectorization/training interfaces under [#1480](https://github.com/Farama-Foundation/PettingZoo/issues/1480); a tracking issue is not itself an implemented replacement.
6. Check public import paths and release support as [#1478](https://github.com/Farama-Foundation/PettingZoo/issues/1478) progresses.

**This page documents currently identified coverage and outstanding work; it does not claim that retirement is already complete.**

## Inventory sources

- SuperSuit exports: [top-level](https://github.com/Farama-Foundation/SuperSuit/blob/main/supersuit/__init__.py), [generic](https://github.com/Farama-Foundation/SuperSuit/blob/main/supersuit/generic_wrappers/__init__.py), [multi-agent](https://github.com/Farama-Foundation/SuperSuit/blob/main/supersuit/multiagent_wrappers/__init__.py), [lambda](https://github.com/Farama-Foundation/SuperSuit/blob/main/supersuit/lambda_wrappers/__init__.py), [vector constructors](https://github.com/Farama-Foundation/SuperSuit/blob/main/supersuit/vector/vector_constructors.py), and [AEC vector](https://github.com/Farama-Foundation/SuperSuit/blob/main/supersuit/aec_vector/__init__.py).
- [PettingZoo native wrapper exports](https://github.com/Farama-Foundation/PettingZoo/blob/main/pettingzoo/utils/wrappers/__init__.py).
- Migration discussions: [#1365](https://github.com/Farama-Foundation/PettingZoo/issues/1365), [#1481](https://github.com/Farama-Foundation/PettingZoo/issues/1481), [#1480](https://github.com/Farama-Foundation/PettingZoo/issues/1480).
