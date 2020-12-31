import pettingzoo
from pettingzoo.utils import agent_selector
import warnings
import inspect
import numpy as np
from copy import copy
import gym
import random
import re
import os
from pettingzoo.utils.env_logger import EnvLogger


def test_bad_close(env):
    EnvLogger.suppress_output()
    EnvLogger.flush()
    e1 = copy(env)
    # test that immediately closing the environment does not crash
    try:
        e1.close()
    except Exception as e:
        warnings.warn("Immediately closing a newly initialized environment should not crash with {}".format(e))

    # test that closing twice does not crash

    e2 = copy(env)
    if "render.modes" in e2.metadata and len(e2.metadata["render.modes"]) > 0:
        e2.reset()
        e2.render()
        e2.close()
        try:
            e2.close()
        except Exception as e:
            warnings.warn("Closing an already closed environment should not crash with {}".format(e))
    EnvLogger.unsuppress_output()


def test_warnings(env):
    EnvLogger.suppress_output()
    EnvLogger.flush()
    e1 = copy(env)
    e1.reset()
    e1.close()
    # e1 should throw a close_unrendered_environment warning
    if len(EnvLogger.mqueue) == 0:
        warnings.warn("env does not warn when closing unrendered env. Should call EnvLogger.warn_close_unrendered_env")
    EnvLogger.unsuppress_output()


def check_asserts(fn, message=None):
    try:
        fn()
        return False
    except AssertionError as e:
        if message is not None:
            return message == str(e)
        return True
    except Exception as e:
        raise e


def check_excepts(fn):
    try:
        fn()
        return False
    except Exception:
        return True


# yields length of mqueue
def check_warns(fn, message=None):
    EnvLogger.suppress_output()
    EnvLogger.flush()
    fn()
    EnvLogger.unsuppress_output()
    if message is None:
        return EnvLogger.mqueue
    else:
        for item in EnvLogger.mqueue:
            if message in item:
                return True
        return False


def test_requires_reset(env):
    if not check_excepts(lambda: env.agent_selection):
        warnings.warn("env.agent_selection should not be defined until reset is called")
    if not check_excepts(lambda: env.dones):
        warnings.warn("env.dones should not be defined until reset is called")
    if not check_excepts(lambda: env.rewards):
        warnings.warn("env.rewards should not be defined until reset is called")
    first_agent = list(env.action_spaces.keys())[0]
    first_action_space = env.action_spaces[first_agent]
    if not check_asserts(lambda: env.step(first_action_space.sample()), "reset() needs to be called before step"):
        warnings.warn("env.step should call EnvLogger.error_step_before_reset if it is called before reset")
    if not check_asserts(lambda: env.observe(first_agent), "reset() needs to be called before observe"):
        warnings.warn("env.observe should call EnvLogger.error_observe_before_reset if it is called before reset")
    if "render.modes" in env.metadata and len(env.metadata["render.modes"]) > 0:
        if not check_asserts(lambda: env.render(), "reset() needs to be called before render"):
            warnings.warn("env.render should call EnvLogger.error_render_before_reset if it is called before reset")
    if not check_warns(lambda: env.close(), "reset() needs to be called before close"):
        warnings.warn("env should warn_close_before_reset() if closing before reset()")


def test_bad_actions(env):
    env.reset()
    first_action_space = env.action_spaces[env.agent_selection]

    if isinstance(first_action_space, gym.spaces.Box):
        try:
            if not check_warns(lambda: env.step(np.nan * np.ones_like(first_action_space.low)), "[WARNING]: Received an NaN"):
                warnings.warn("NaN actions should call EnvLogger.warn_action_is_NaN")
        except Exception:
            warnings.warn("nan values should not raise an error, instead, they should call EnvLogger.warn_action_is_NaN and instead perform some reasonable action, (perhaps the all zeros action?)")

        env.reset()
        if np.all(np.greater(first_action_space.low.flatten(), -1e10)):
            small_value = first_action_space.low - 1e10
            try:
                if not check_warns(lambda: env.step(small_value), "[WARNING]: Received an action"):
                    warnings.warn("out of bounds actions should call EnvLogger.warn_action_out_of_bound")
            except Exception:
                warnings.warn("out of bounds actions should not raise an error, instead, they should call EnvLogger.warn_action_out_of_bound and instead perform some reasonable action, (perhaps the all zeros action?)")

        if not check_excepts(lambda: env.step(np.ones((29, 67, 17)))):
            warnings.warn("actions of a shape not equal to the box should fail with some useful error")
    elif isinstance(first_action_space, gym.spaces.Discrete):
        try:
            if not check_warns(lambda: env.step(np.nan), "[WARNING]: Received an NaN"):
                warnings.warn("nan actions should call EnvLogger.warn_action_is_NaN, and instead perform some reasonable action (perhaps the do nothing action?  Or perhaps the same behavior as an illegal action?)")
        except Exception:
            warnings.warn("nan actions should not raise an error, instead, they should call EnvLogger.warn_action_is_NaN and instead perform some reasonable action (perhaps the do nothing action?  Or perhaps the same behavior as an illegal action?)")

        env.reset()
        try:
            if not check_asserts(lambda: env.step(first_action_space.n)):
                warnings.warn("out of bounds actions should assert")
        except Exception:
            warnings.warn("out of bounds actions should assert")

    env.reset()

    # test illegal actions
    first_agent = env.agent_selection
    info = env.infos[first_agent]
    action_space = env.action_spaces[first_agent]
    if 'legal_moves' in info:
        legal_moves = info['legal_moves']
        illegal_moves = set(range(action_space.n)) - set(legal_moves)

        if len(illegal_moves) > 0:
            illegal_move = list(illegal_moves)[0]
            if not check_warns(lambda: (env.step(illegal_move)), "[WARNING]: Illegal"):
                warnings.warn("If an illegal move is made, warning should be generated by calling EnvLogger.warn_on_illegal_move")
            if not env.dones[first_agent]:
                warnings.warn("Environment should terminate after receiving an illegal move")
        else:
            warnings.warn("The legal moves were just all possible moves. This is very usual")

    env.reset()


def error_test(env):
    print("Starting Error test")
    env_warnings = copy(env)
    env_bad_close = copy(env)

    test_warnings(env_warnings)
    # do this before reset
    test_requires_reset(env)

    test_bad_actions(env)

    test_bad_close(env_bad_close)

    print("Passed Error test")
