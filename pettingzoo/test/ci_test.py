import sys
from .api_test import api_test
from .performance_benchmark import performance_benchmark
from .manual_control_test import manual_control_test
from .all_modules import all_environments, manual_environments
from .all_modules import all_prefixes
from .render_test import render_test
from .seed_test import seed_test
from .save_obs_test import test_save_obs
from .max_cycles_test import max_cycles_test
from .parallel_test import parallel_api_test

assert len(sys.argv) == 7, "ci_test expects 5 arguments: env_id, num_cycles, render, manual_control, performance, save_obs"

num_cycles = int(sys.argv[2])
render = sys.argv[3] == 'True'
manual_control = sys.argv[4] == 'True'
performance = sys.argv[5] == 'True'
save_obs = sys.argv[6] == 'True'


env_id = sys.argv[1]


def perform_ci_test(env_id, num_cycles, render, manual_control, performance, save_obs):
    print("running game {}".format(env_id))
    env_module = all_environments[env_id]
    _env = env_module.env()
    error_collected = []
    try:
        api_test(_env, num_cycles=num_cycles, render=render, verbose_progress=True)
    except Exception as e:
        error_collected.append("API Test: " + str(e))

    if "classic/" not in env_id:
        parallel_api_test(env_module.parallel_env(), num_cycles=num_cycles)

    if "prospector" not in env_id:
        seed_test(env_module.env, num_cycles)

    if "classic/" not in env_id:
        max_cycles_test(env_module)

    # error_test(env_module.env())

    if save_obs:
        test_save_obs(_env)

    if render:
        try:
            assert len(_env.metadata.get('render.modes')) >= 2
            render_test(_env)
        except Exception as e:
            error_collected.append("Render Test:" + str(e))

    if manual_control and env_id in manual_environments:
        try:
            manual_control_fn = env_module.manual_control
            manual_control_test(manual_control_fn)
        except Exception as e:
            error_collected.append("Manual Control: " + str(e))

    if performance:
        _env = env_module.env()
        performance_benchmark(_env)

    return error_collected


if env_id in all_prefixes:
    warning_map = {}
    for e in all_environments:
        if e.startswith(env_id):
            warning_map[e] = perform_ci_test(e, num_cycles, render, manual_control, performance, save_obs)
    f = open("test_output.txt", "w")
    for warn in warning_map:
        warn_list = warning_map[warn]
        if len(warn_list) > 0:
            for w in warn_list:
                f.write(warn + ": " + w + "\n")
else:
    print("Environment: '{}' not in the 'all_environments' list".format(env_id))
