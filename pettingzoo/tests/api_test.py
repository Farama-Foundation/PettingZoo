import pettingzoo
from pettingzoo.utils import agent_selector
import warnings
import inspect
import numpy as np
from copy import copy
import gym
import random
import re
from skimage.io import imsave
import os


def test_obervation(observation, observation_0):
    if isinstance(observation, np.ndarray):
        if np.isinf(observation).any():
            warnings.warn("Observation contains infinity (np.inf) or negative infinity (-np.inf)")
        if np.isnan(observation).any():
            warnings.warn("Observation contains NaNs")
        if len(observation.shape) > 3:
            warnings.warn("Observation has more than 3 dimensions")
        if observation.shape == (0,):
            assert False, "Observation can not be an empty array"
        if observation.shape == (1,):
            warnings.warn("Observation is a single number")
        if not isinstance(observation, observation_0.__class__):
            warnings.warn("Observations between agents are different classes")
        if (observation.shape != observation_0.shape) and (len(observation.shape) == len(observation_0.shape)):
            warnings.warn("Observations are different shapes")
        if len(observation.shape) != len(observation_0.shape):
            warnings.warn("Observations have different number of dimensions")
        if not np.can_cast(observation.dtype, np.dtype("float64")):
            warnings.warn("Observation numpy array is not a numeric dtype")
        if np.array_equal(observation, np.zeros(observation.shape)):
            warnings.warn("Observation numpy array is all zeros.")
        if not np.all(observation >= 0) and ((len(observation.shape) == 2) or (len(observation.shape) == 3 and observation.shape[2] == 1) or (len(observation.shape) == 3 and observation.shape[2] == 3)):
            warnings.warn("The observation contains negative numbers and is in the shape of a graphical observation. This might be a bad thing.")
    else:
        warnings.warn("Observation is not NumPy array")


def test_observation_action_spaces(env, agent_0):
    assert isinstance(env.action_spaces, dict), "action_spaces must be a dict"
    assert isinstance(env.observation_spaces, dict), "observation_spaces must be a dict"
    assert len(env.observation_spaces) == len(env.action_spaces) == len(env.agents), "observation_spaces, action_spaces, and agents must have the same length"

    for agent in env.agents:
        assert isinstance(env.observation_spaces[agent], gym.spaces.Space), "Observation space for each agent must extend gym.spaces.Space"
        assert isinstance(env.action_spaces[agent], gym.spaces.Space), "Agent space for each agent must extend gym.spaces.Space"
        if not (isinstance(env.observation_spaces[agent], gym.spaces.Box) or isinstance(env.observation_spaces[agent], gym.spaces.Discrete)):
            warnings.warn("Observation space for each agent probably should be gym.spaces.box or gym.spaces.discrete")
        if not (isinstance(env.action_spaces[agent], gym.spaces.Box) or isinstance(env.action_spaces[agent], gym.spaces.Discrete)):
            warnings.warn("Action space for each agent probably should be gym.spaces.box or gym.spaces.discrete")
        if (not isinstance(agent, str)) and agent != 'env':
            warnings.warn("Agent's are recommended to have numbered string names, like player_0")
        if not isinstance(agent, str) or not re.match("[a-z]+_[0-9]+", agent):  # regex for ending in _<integer>
            warnings.warn("We recommend agents to be named in the format <descriptor>_<number>, like \"player_0\"")
        if not isinstance(env.observation_spaces[agent], env.observation_spaces[agent_0].__class__):
            warnings.warn("The class of observation spaces is different between two agents")
        if not isinstance(env.action_spaces[agent], env.action_spaces[agent_0].__class__):
            warnings.warn("The class of action spaces is different between two agents")
        if env.observation_spaces[agent] != env.observation_spaces[agent_0]:
            warnings.warn("Agents have different observation space sizes")
        if env.action_spaces[agent] != env.action_spaces[agent_0]:
            warnings.warn("Agents have different action space sizes")

        if isinstance(env.action_spaces[agent], gym.spaces.Box):
            if np.any(np.equal(env.action_spaces[agent].low, -np.inf)):
                warnings.warn("Agent's minimum action space value is -infinity. This is probably too low.")
            if np.any(np.equal(env.action_spaces[agent].high, np.inf)):
                warnings.warn("Agent's maxmimum action space value is infinity. This is probably too high")
            if np.any(np.equal(env.action_spaces[agent].low, env.action_spaces[agent].high)):
                warnings.warn("Agent's maximum and minimum action space values are equal")
            if np.any(np.greater(env.action_spaces[agent].low, env.action_spaces[agent].high)):
                assert False, "Agent's minimum action space value is greater than it's maximum"
            if env.action_spaces[agent].low.shape != env.action_spaces[agent].shape:
                assert False, "Agent's action_space.low and action_space have different shapes"
            if env.action_spaces[agent].high.shape != env.action_spaces[agent].shape:
                assert False, "Agent's action_space.high and action_space have different shapes"

        if isinstance(env.observation_spaces[agent], gym.spaces.Box):
            if np.any(np.equal(env.observation_spaces[agent].low, -np.inf)):
                warnings.warn("Agent's minimum observation space value is -infinity. This is probably too low.")
            if np.any(np.equal(env.observation_spaces[agent].high, np.inf)):
                warnings.warn("Agent's maxmimum observation space value is infinity. This is probably too high")
            if np.any(np.equal(env.observation_spaces[agent].low, env.observation_spaces[agent].high)):
                warnings.warn("Agent's maximum and minimum observation space values are equal")
            if np.any(np.greater(env.observation_spaces[agent].low, env.observation_spaces[agent].high)):
                assert False, "Agent's minimum observation space value is greater than it's maximum"
            if env.observation_spaces[agent].low.shape != env.observation_spaces[agent].shape:
                assert False, "Agent's observation_space.low and observation_space have different shapes"
            if env.observation_spaces[agent].high.shape != env.observation_spaces[agent].shape:
                assert False, "Agent's observation_space.high and observation_space have different shapes"


def test_reward(reward):
    if not (isinstance(reward, int) or isinstance(reward, float)) and not isinstance(np.dtype(reward), np.dtype) and not isinstance(reward, np.ndarray):
        warnings.warn("Reward should be int, float, NumPy dtype or NumPy array")
    if isinstance(reward, np.ndarray):
        if isinstance(reward, np.ndarray) and not reward.shape == (1,):
            assert False, "Rewards can only be one number"
        if np.isinf(reward):
            assert False, "Reward must be finite"
        if np.isnan(reward):
            assert False, "Rewards cannot be NaN"
        if not np.can_cast(reward.dtype, np.dtype("float64")):
            assert False, "Reward NumPy array is not a numeric dtype"


def test_rewards_dones(env, agent_0):
    for agent in env.agents:
        assert isinstance(env.dones[agent], bool), "Agent's values in dones must be True or False"
        assert isinstance(env.rewards[agent], env.rewards[agent_0].__class__), "Rewards for each agent must be of the same class"
        test_reward(env.rewards[agent])


def play_test(env, observation_0):
    prev_observe = env.reset()
    for agent in env.agent_order:  # step through every agent once with observe=True
        if 'legal_moves' in env.infos[agent]:
            action = random.choice(env.infos[agent]['legal_moves'])
        else:
            action = env.action_spaces[agent].sample()
        next_observe = env.step(action)
        if not env.observation_spaces[agent].contains(prev_observe):
            print("Out of bounds observation: ", prev_observe)
        assert env.observation_spaces[agent].contains(prev_observe), "Agent's observation is outside of it's observation space"
        test_obervation(prev_observe, observation_0)
        prev_observe = next_observe
        if not isinstance(env.infos[agent], dict):
            warnings.warn("The info of each agent should be a dict, use {} if you aren't using info")
        assert env.num_agents == len(env.agents), "env.num_agents is not equal to len(env.agents)"

    env.reset()
    reward_0 = env.rewards[env.agent_order[0]]
    for agent in env.agent_order:  # step through every agent once with observe=False
        if 'legal_moves' in env.infos[agent]:
            action = random.choice(env.infos[agent]['legal_moves'])
        else:
            action = env.action_spaces[agent].sample()
        reward, done, info = env.last()
        assert isinstance(done, bool), "Done from last is not True or False"
        assert reward == env.rewards[agent], "Reward from last() and rewards[agent] do not match"
        assert done == env.dones[agent], "Done from last() and rewards[agent] do not match"
        assert info == env.infos[agent], "Info from last() and infos[agent] do not match"
        assert isinstance(env.rewards[agent], reward_0.__class__), "Rewards for each agent must be of the same class"
        test_reward(reward)
        observation = env.step(action, observe=False)
        assert observation is None, "step(observe=False) must not return anything"


def test_observe(env, observation_0, save_obs):
    if save_obs:
        save_obs_folder = "saved_observations/{}".format(env.__module__)
        os.makedirs(save_obs_folder, exist_ok=True)

    for agent in env.agent_order:
        observation = env.observe(agent)
        test_obervation(observation, observation_0)
        if save_obs:
            fname = os.path.join(save_obs_folder, str(agent) + '.png')
            imsave(fname, observation)


def test_render(env):
    render_modes = env.metadata.get('render.modes')
    assert render_modes is not None, "Environment's that support rendering must define render modes in metadata"
    env.reset(observe=False)
    for mode in render_modes:
        for _ in range(10):
            for agent in env.agent_order:
                if 'legal_moves' in env.infos[agent]:
                    action = random.choice(env.infos[agent]['legal_moves'])
                else:
                    action = env.action_spaces[agent].sample()
                env.step(action, observe=False)
                env.render(mode=mode)
                if all(env.dones.values()):
                    env.reset()
                    break


def test_agent_selector(env):
    if not hasattr(env, "_agent_selector"):
        warnings.warn("Env has no object named _agent_selector. We recommend handling agent cycling with the agent_selector utility from utils/agent_selector.py.")
        return

    if not isinstance(env._agent_selector, agent_selector):
        warnings.warn("You created your own agent_selector utility. You might want to use ours, in utils/agent_selector.py")
        return

    assert hasattr(env, "agent_order"), "Env does not have agent_order"

    env.reset(observe=False)
    agent_order = copy(env.agent_order)
    _agent_selector = agent_selector(agent_order)
    agent_selection = _agent_selector.next()
    assert env._agent_selector == _agent_selector, "env._agent_selector is initialized incorrectly"
    assert env.agent_selection == agent_selection, "env.agent_selection is not the same as the first agent in agent_order"

    for _ in range(200):
        agent = agent_selection
        if 'legal_moves' in env.infos[agent]:
            action = random.choice(env.infos[agent]['legal_moves'])
        else:
            action = env.action_spaces[agent].sample()
        env.step(action, observe=False)

        if all(env.dones.values()):
            break

        if agent_order == env.agent_order:
            agent_selection = _agent_selector.next()
            assert env.agent_selection == agent_selection, "env.agent_selection ({}) is not the same as the next agent in agent_order {}".format(env.agent_selection, env.agent_order)
        else:
            previous_agent_selection_index = agent_order.index(agent_selection)
            agent_order = copy(env.agent_order)
            _agent_selector.reinit(agent_order)
            skips = (previous_agent_selection_index + 1) % len(env.agents)
            for _ in range(skips + 1):
                agent_selection = _agent_selector.next()
            assert env.agent_selection == agent_selection, "env.agent_selection ({}) is not the same as the next agent in agent_order {}".format(env.agent_selection, env.agent_order)


def test_warnings(env):
    from pettingzoo.utils import EnvLogger
    EnvLogger.suppress_output()
    EnvLogger.flush()
    e1 = copy(env)
    e1.reset()
    e1.close()
    # e1 should throw a close_unrendered_environment warning
    if len(EnvLogger.mqueue) == 0:
        warnings.warn("env does not warn when closing unrendered env. Should call EnvLogger.warn_close_unrendered_env")
    EnvLogger.unsuppress_output()


def inp_handler(name):
    from pynput.keyboard import Key, Controller as KeyboardController
    import time

    keyboard = KeyboardController()
    time.sleep(0.1)
    choices = ['w', 'a', 's', 'd', 'j', 'k', Key.left, Key.right, Key.up, Key.down]
    NUM_TESTS = 50
    for x in range(NUM_TESTS):
        i = random.choice(choices) if x != NUM_TESTS - 1 else Key.esc
        keyboard.press(i)
        time.sleep(0.1)
        keyboard.release(i)


def test_manual_control(manual_control):
    import threading
    manual_in_thread = threading.Thread(target=inp_handler, args=(1,))

    manual_in_thread.start()

    try:
        manual_control()
    except Exception:
        raise Exception("manual_control() has crashed. Please fix it.")

    manual_in_thread.join()


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
def check_warns(fn,message=None):
    from pettingzoo.utils import EnvLogger
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
    if not check_excepts(lambda: env.infos):
        warnings.warn("env.infos should not be defined until reset is called")
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
        if np.all(np.greater(first_action_space.low.flatten(),-1e10)):
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
            if not check_warns(lambda: env.step(first_action_space.n)):
                warnings.warn("out of bounds actions should call EnvLogger.warn_discrete_out_of_bound")
        except Exception:
            warnings.warn("out of bounds actions should not raise an error, instead, they should call EnvLogger.warn_discrete_out_of_bound and instead perform some reasonable action (perhaps the do nothing action if your environment has one? Or perhaps the same behavior as an illegal action?)")


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
            if not check_warns(lambda: env.step(env.step(illegal_move)),"[WARNING]: Illegal"):
                warnings.warn("if illegal move is made, warning should be generated by calling EnvLogger.warn_on_illegal_move")
            if not env.dones[first_agent]:
                warnings.warn("game should terminate after making an illegal move")
        else:
            warnings.warn("legal moves is all possible moves. This is very unsual.")

    env.reset()


def check_environment_args(env):
    args = inspect.getfullargspec(env.__init__)
    if len(args.args) < 2 or "seed" != args.args[1]:
        warnings.warn("environment does not have a `seed` parameter as its first argument. It should have a seed if the environment uses any randomness")
    else:
        def hash_obsevation(obs):
            try:
                val = hash(obs.tobytes())
                return val
            except AttributeError:
                try:
                    return hash(obs)
                except TypeError:
                    warnings.warn("observation not an int or an ndarray")
                    return 0

        # checks deterministic behavior if seed is set
        base_seed = 192312
        new_env = env.__class__(seed=base_seed)
        actions = {agent: space.sample() for agent, space in new_env.action_spaces.items()}
        hashes = []
        num_seeds = 5
        rand_seeds = [random.randint(0, 1000000) for _ in range(num_seeds)]
        for x in range(num_seeds):
            cur_hashes = []
            random.seed(rand_seeds[x])
            np.random.seed(rand_seeds[x])
            obs = new_env.reset()
            cur_hashes.append(hash_obsevation(obs))
            for _ in range(50):
                rew, done, info = new_env.last()
                if done:
                    break
                next_obs = new_env.step(actions[new_env.agent_selection])
                cur_hashes.append(hash_obsevation(next_obs))

            hashes.append(hash(tuple(cur_hashes)))
            new_env = env.__class__(seed=base_seed)
        if not all(hashes[0] == h for h in hashes):
            warnings.warn("seeded environment is not fully deterministic, depends on random.seed or numpy.random.seed")


def api_test(env, render=False, manual_control=None, save_obs=False):
    print("Starting API test")
    env_agent_sel = copy(env)
    env_warnings = copy(env)

    assert isinstance(env, pettingzoo.AECEnv), "Env must be an instance of pettingzoo.AECEnv"

    # do this before reset
    test_requires_reset(env)

    check_environment_args(env)

    observation = env.reset(observe=False)
    assert observation is None, "reset(observe=False) must not return anything"
    assert not any(env.dones.values()), "dones must all be False after reset"

    assert isinstance(env.num_agents, int), "num_agents must be an integer"
    assert env.num_agents != 0, "Your environment should have nonzero number of agents"
    assert env.num_agents > 0, "Your environment can't have a negative number of agents"

    observation_0 = env.reset()
    test_obervation(observation_0, observation_0)

    if save_obs:
        for agent in env.agents:
            assert isinstance(env.observation_spaces[agent], gym.spaces.Box), "Observations must be Box to save observations as image"
            assert np.all(np.equal(env.observation_spaces[agent].low, 0)) and np.all(np.equal(env.observation_spaces[agent].high, 255)), "Observations must be 0 to 255 to save as image"
            assert len(env.observation_spaces[agent].shape) == 3 or len(env.observation_spaces[agent].shape) == 2, "Observations must be 2D or 3D to save as image"
            if len(env.observation_spaces[agent].shape) == 3:
                assert env.observation_spaces[agent].shape[2] == 1 or env.observation_spaces[agent].shape[2] == 3, "3D observations can only have 1 or 3 channels to save as an image"

    assert isinstance(env.agent_order, list), "agent_order must be a list"

    agent_0 = env.agent_order[0]

    test_observation_action_spaces(env, agent_0)

    play_test(env, observation_0)

    test_bad_actions(env)

    assert isinstance(env.rewards, dict), "rewards must be a dict"
    assert isinstance(env.dones, dict), "dones must be a dict"
    assert isinstance(env.infos, dict), "infos must be a dict"

    assert len(env.rewards) == len(env.dones) == len(env.infos) == len(env.agents), "rewards, dones, infos and agents must have the same length"

    test_rewards_dones(env, agent_0)

    test_observe(env, observation_0, save_obs=save_obs)

    test_agent_selector(env_agent_sel)

    test_warnings(env_warnings)

    if render:
        test_render(env)

    if manual_control is not None:
        test_manual_control(manual_control)
    else:
        env.close()

    # test that if env has overridden render(), they must have overridden close() as well
    base_render = pettingzoo.utils.env.AECEnv.render
    base_close = pettingzoo.utils.env.AECEnv.close
    if base_render != env.__class__.render:
        assert (base_close != env.__class__.close), "If render method defined, then close method required"
    else:
        warnings.warn("environment has not defined a render() method")

    print("Passed API test")
