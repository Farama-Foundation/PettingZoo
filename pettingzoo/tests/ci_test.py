import pettingzoo.tests.api_test as api_test
import pettingzoo.tests.bombardment_test as bombardment_test
import pettingzoo.tests.performance_benchmark as performance_benchmark
import sys
from all_envs import all_environments

# classic
_manual_control = None

render = False
if sys.argv[2] == 'True':
    render = True
manual_control = False
if sys.argv[3] == 'True':
    manual_control = True
bombardment = False
if sys.argv[4] == 'True':
    bombardment = True
performance = False
if sys.argv[5] == 'True':
    performance = True
save_obs = False
if sys.argv[6] == 'True':
    save_obs = True

env_id = sys.argv[1]
if env_id in all_environments:
    env_module = all_environments[env_id]
    _env = env_module.env()
    manual_control = getattr(env_module,"manual_control",None)
    api_test.api_test(_env, render=render, manual_control=manual_control, save_obs=False)
    if
        performance_benchmark.performance_benchmark(_env)

if sys.argv[1] == 'classic/backgammon':
    print('classic/backgammon')
    from pettingzoo.classic import backgammon_v0
    _env = backgammon_v0.env()
    api_test.api_test(_env, render=render, manual_control=None, save_obs=False)
    if bombardment:
        _env = backgammon_v0.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = backgammon_v0.env()
        performance_benchmark.performance_benchmark(_env)
    print('')

elif sys.argv[1] == 'sisl/pursuit':
    print('sisl/pursuit')
    from pettingzoo.sisl import pursuit_v0
    _env = pursuit_v0.env()
    if manual_control:
        _manual_control = pursuit_v0.manual_control
    api_test.api_test(_env, render=render, manual_control=_manual_control, save_obs=False)
    if bombardment:
        _env = pursuit_v0.env()
        bombardment_test.bombardment_test(_env)
    if performance:
        _env = pursuit_v0.env()
        performance_benchmark.performance_benchmark(_env)
    print('')
