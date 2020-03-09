import time


def performance_benchmark(env):
    cycles = 0
    turn = 0
    _ = env.reset()
    start = time.time()
    end = 0

    while True:
        for agent in env.agent_order:  # step through every agent once with observe=True
            action = env.action_spaces[agent].sample()
            _ = env.step(action)
            turn += 1
        cycles += 1
        if time.time() - start > 60:
            end = time.time()
            break
        if all(env.dones.values()):
            _ = env.reset()

    length = end - start

    turns_per_time = turn / length
    cycles_per_time = cycles / length
    print(str(turns_per_time) + " turns per second")
    print(str(cycles_per_time) + " cycles per second")
