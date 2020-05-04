import pettingzoo.tests.api_test as api_test
import pettingzoo.tests.bombardment_test as bombardment_test
import pettingzoo.tests.performance_benchmark as performance_benchmark
import pettingzoo.tests.manual_control_test as test_manual_control
from pettingzoo.utils import save_observation
import sys
from .all_modules import all_environments
from .render_test import test_render


render = sys.argv[2] == 'True'
manual_control = sys.argv[3] == 'True'
bombardment = sys.argv[4] == 'True'
performance = sys.argv[5] == 'True'
save_obs = sys.argv[6] == 'True'


env_id = sys.argv[1]
if env_id in all_environments:
    env_module = all_environments[env_id]
    _env = env_module.env()
    api_test.api_test(_env, render=render)
    if save_obs:
        for agent in _env.agent_order:
            observation = env.observe(agent)
            if save_obs:
                save_observation(env=_env, agent=agent, save_dir="saved_observations")

    if render:
        test_render(_env)

    if manual_control:
        manual_control_fn = getattr(env_module,"manual_control",None)
        if manual_control_fn is not None:
            test_manual_control(manual_control_fn)

    if performance:
        _env = env_module.env()
        performance_benchmark.performance_benchmark(_env)

    if bombardment:
        _env = env_module.env()
        bombardment_test.bombardment_test(_env)
else:
    print("Environment: '{}' not in the 'all_environments' list".format(env_id))
