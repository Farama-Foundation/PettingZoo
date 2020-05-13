import pettingzoo.tests.api_test as api_test
import pettingzoo.tests.bombardment_test as bombardment_test
import pettingzoo.tests.performance_benchmark as performance_benchmark
import pettingzoo.tests.manual_control_test as test_manual_control

import sys
from .all_modules import all_environments
from .render_test import test_render
from .error_tests import error_test
from .seed_test import seed_test
from .save_obs_test import test_save_obs

render = sys.argv[2] == 'True'
manual_control = sys.argv[3] == 'True'
bombardment = sys.argv[4] == 'True'
performance = sys.argv[5] == 'True'
save_obs = sys.argv[6] == 'True'


env_id = sys.argv[1]
if env_id in all_environments:
    print("running game {}".format(env_id))
    env_module = all_environments[env_id]
    _env = env_module.raw_env()
    api_test.api_test(_env, render=render, verbose_progress=True)

    seed_test(env_module.env)
    # error_test(env_module.env())

    if save_obs:
        test_save_obs(_env)

    if render:
        test_render(_env)

    if manual_control:
        manual_control_fn = getattr(env_module, "manual_control", None)
        if manual_control_fn is not None:
            test_manual_control.test_manual_control(manual_control_fn)

    if performance:
        _env = env_module.env()
        performance_benchmark.performance_benchmark(_env)

    if bombardment:
        _env = env_module.env()
        bombardment_test.bombardment_test(_env)
else:
    print("Environment: '{}' not in the 'all_environments' list".format(env_id))
