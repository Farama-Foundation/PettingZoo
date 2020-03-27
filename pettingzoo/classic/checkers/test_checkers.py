import sys
sys.path.append("/home/bws4/Desktop/PettingZoo-master")

import checkers
import numpy as np


if __name__ == '__main__':
    
    env = checkers.env()
    print("Empty board: ")
    env.ch.print_empty_board()
    #env.ch.print_board()
    #print(env.agents)
    #print(env.infos[env.agent_selection]['legal_moves'][0])
    #env.step((9,13))
    #env.step((21,17))

    seed = 4
    
    while env.winner == -1 and env.num_moves < env.num_moves_max:
        #action = env.infos[env.agent_selection]['legal_moves'][0]
        actions = env.infos[env.agent_selection]['legal_moves']
        random_selection = np.random.RandomState(seed=seed)
        action = random_selection.choice(np.asarray(actions, dtype='int,int'))
        env.step(action)
    
    #print(env.winner)
    print(env.rewards)
    
    
    """
    _env = checkers.env()
    api_test.api_test(_env, render=True, manual_control=False)
    #_env = checkers.env()
    #bombardment_test.bombardment_test(_env)
    #_env = checkers.env()
    #performance_benchmark.performance_benchmark(_env)
    """
    
    
    


    
    