import sys
import time
import random
import numpy as np


def _performance_benchmark(env, single_run_time):
    cycles = 0
    turn = 0
    _ = env.reset()
    start = time.process_time()
    end = 0

    while True:
        cycles += 1
        for agent in env.agent_iter(env.num_agents):  # step through every agent once with observe=True
            reward, done, info = env.last()
            if not done and 'legal_moves' in env.infos[agent]:
                action = random.choice(env.infos[agent]['legal_moves'])
            else:
                action = env.action_spaces[agent].sample()
            _ = env.step(action)
            turn += 1

            if all(env.dones.values()):
                _ = env.reset()

        if time.process_time() - start > single_run_time:
            end = time.process_time()
            break

    length = end - start

    turns_per_time = turn / length
    cycles_per_time = cycles / length

    return cycles_per_time, turns_per_time


def _check_benchmark_stability(name, arr):
    # Stability check based on the pyperf standard at
    # https://pyperf.readthedocs.io/en/latest/cli.html#pyperf-check
    mean = arr.mean()
    std = arr.std()

    if (std > mean / 10):
        # Warn if the standard deviation is greater than 10% of the mean
        print(f"[WARNING] for {name} Standard deviation is greater than 10% of mean", file=sys.stderr)

    if (arr.min() < mean / 2):
        # Warn if the minimum is 50% smaller than the mean
        print(f"[WARNING] for {name} minimum is 50% smaller than the mean", file=sys.stderr)

    if (arr.max() > 1.5 * mean):
        # Warn if the maximum is 50% greater than the mean
        print(f"[WARNING] for {name} maximum is 50% greater than the mean", file=sys.stderr)


def performance_benchmark(env, overall_test_time=5, single_run_time=1, check_benchmark_stability=True):
    print("Starting performance benchmark")

    assert overall_test_time % single_run_time == 0, "'overall_test_time' should be a multiple of 'single_run_time'"

    cycles_times = []
    turns_times = []
    for test_idx in range(int(overall_test_time / single_run_time)):
        cycle_time, turns_time = _performance_benchmark(env, single_run_time)
        turns_times.append(turns_time)
        cycles_times.append(cycle_time)

    turns_times = np.array(turns_times)
    cycles_times = np.array(cycles_times)

    if (check_benchmark_stability):
        _check_benchmark_stability("turns", turns_times)
        _check_benchmark_stability("cycles", cycles_times)

    print("{0:.2f} +- {1:.2f} turns  per second".format(turns_times.mean(), turns_times.std()))
    print("{0:.2f} +- {1:.2f} cycles per second".format(cycles_times.mean(), cycles_times.std()))
