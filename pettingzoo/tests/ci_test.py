import pettingzoo.tests.api_test as api_test
import pettingzoo.tests.bombardment_test as bombardment_test
import pettingzoo.tests.performance_benchmark as performance_benchmark
import pettingzoo.tests.manual_control_test as test_manual_control

import sys
from .all_modules import all_environments
from .all_modules import all_prefixes
from .render_test import test_render
from .error_tests import error_test
from .seed_test import seed_test
from .save_obs_test import test_save_obs
from flake8.api import legacy as flake8

render = sys.argv[2] == 'True'
manual_control = sys.argv[3] == 'True'
bombardment = sys.argv[4] == 'True'
performance = sys.argv[5] == 'True'
save_obs = sys.argv[6] == 'True'


env_id = sys.argv[1]


def perform_ci_test(env_id, render, manual_control, bombardment, performance, save_obs):
    print("running game {}".format(env_id))
    env_module = all_environments[env_id]
    _env = env_module.env()
    warning_list = api_test.api_test(_env, render=render, verbose_progress=True)

    seed_test(env_module.env)
    # error_test(env_module.env())

    if save_obs:
        test_save_obs(_env)

    if render:
        test_render(_env)

    if manual_control:
        manual_control_fn = getattr(env_module, "manual_control", None)
        if manual_control_fn is not None:
            status = test_manual_control.test_manual_control(manual_control_fn)
            if status != 0:
                warning_list.append("Manual Control test failed")

    if performance:
        _env = env_module.env()
        performance_benchmark.performance_benchmark(_env)

    if bombardment:
        _env = env_module.env()
        bombardment_test.bombardment_test(_env, cycles=7000)

    # flake8 test
    style_guide = flake8.get_style_guide(ignore=["E501", "E731", "E741", "E402", "F401", "W503"])
    file_name = "pettingzoo/" + env_id
    report = style_guide.check_files([file_name])
    if report.total_errors > 0:
        warning_list.append("Flake8 test failed")

    return warning_list


if env_id in all_prefixes:
    warning_map = {}
    for e in all_environments:
        if e.startswith(env_id):
            warning_map[e] = perform_ci_test(e, render, manual_control, bombardment, performance, save_obs)
    f = open("test_output.txt", "w")
    for warn in warning_map:
        warn_list = warning_map[warn]
        if len(warn_list) > 0:
            log = "Env " + warn + " generated the following errors:\n"
            f.write(log)
            for w in warn_list:
                f.write(w + "\n")
    f.close()
else:
    print("Environment: '{}' not in the 'all_environments' list".format(env_id))
