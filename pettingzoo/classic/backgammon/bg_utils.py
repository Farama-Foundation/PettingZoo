from backgammon import Backgammon as Game, WHITE, BLACK, COLORS
import numpy as np


def get_valid_actions(env, roll):
    a=env.game.get_valid_plays(env.current_agent, roll)
    return a

def get_opponent_agent(env):
    env.current_agent = env.game.get_opponent(env.current_agent)
    return env.current_agent

#action goes from (2,4) list to a tuple or 2 or 4 tuples
def to_bg_format(action):
    acts = [["bar" if x==25 else x for x in t] for t in action]
    acts = [(a, b) for a, b in acts if (a != -2 and b != -2)]
    return acts

#takes list of tuples of tuples (including bar) and converst it to fit in the sction space
def to_gym_format(actions):
    lst = [[[25, b] if a =='bar' else ([a, 25] if b == 'bar' else [a,b])
        for (a,b) in tups] for tups in actions]
    lst = [[[-2,-2],[-2,-2],[-2,-2],[-2,-2]] if len(act) == 0 else
        (act + [[-2,-2],[-2,-2],[-2,-2]] if len(act) == 1 else
        (act + [[-2,-2],[-2,-2]] if len(act) == 2 else
        (act + [[-2,-2]] if len(act) == 3 else act))) for act in lst]
    return np.array(lst)

def valid_action(env, action):
      res = False
      for moves in env.infos[env.agent_selection]['legal_moves']:
          if (len(moves) >=1):
              if moves[0][0] == action[0][0] and moves[0][1] == action[0][1]:
                  if len(moves) >= 2:
                      if moves[1][0] == action[1][0] and moves[1][1] == action[1][1]:
                          if len(moves) >= 3:
                              if moves[2][0] == action[2][0] and moves[2][1] == action[2][1]:
                                  if len(moves) == 4:
                                      if moves[3][0] == action[3][0] and moves[3][1] == action[3][1]:
                                          res = True
                                  else:
                                      res = True
                          else:
                              res = True
                  else:
                      res = True

      return res
