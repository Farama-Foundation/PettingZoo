from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector
from gym import spaces

from .tictactoe_utils import Board

class env(AECEnv):
    metadata = {'render.modes': ['human']} # only add if environment supports rendering

    def __init__(self):
        super(env, self).__init__()
        self.board = Board()

        self.num_agents = 2
        self.agents = list(range(self.num_agents))

        self.agent_order = list(self.agents)
        self._agent_selector = agent_selector(self.agent_order)


        self.action_spaces = {i: spaces.Discrete(9) for i in range(2)}
        self.observation_spaces = {i: spaces.Discrete(9) for i in range(2)}

        self.rewards = {i: 0 for i in range(self.num_agents)}
        self.dones = {i: False for i in range(self.num_agents)}
        self.infos = {i: {'legal_moves': []} for i in range(self.num_agents)}

        self.agent_selection = 0

        self.display_wait = 0.0

        self.reset()


    # returns a flat representation of tic tac toe board
    # ie [1, 0, 0, 0, 0, 0, 0, 2, 0]
    # where indexes are column wise order
    # 1 4 7
    # 2 5 8
    # 3 6 9
    # 
    # Key
    # ----
    # blank space = 0
    # agent 0 = 1
    # agent 1 = 2
    def observe(self, agent):
        # return observation of an agent
        return [square.state for square in self.board.squares]

    # action in this case is a value from 0 to 8 indicating position to move on tic tac toe board
    def step(self, action, observe=True):
        # check if input action is a valid move
        if(self.board.squares[action] == 0):
            # play turn
            self.board.play_turn(self.board.squares[action])

            # update infos
            # ie list of size 9 where 1 represents valid move, 0 is invalid move.
            self.infos[self.agent_selection] = [1 if not i else 0 for i in self.board.squares]

            # check if game over
            game_over = all(square.state in [1, 2] for square in self.squares)

            # if winner = 0 no winner yet
            # if winner = 1 agent 0 won
            # if winner = 2 agent 1 won
            winner = self.board.check_for_winner()

            if game_over:
                if winner == 0:
                    # tie
                    pass
                elif winner == 1:
                    # agent 0 won
                    self.rewards[0] += 100
                    self.rewards[1] -= 100
                else:
                    # agent 1 won
                    self.rewards[1] += 100
                    self.rewards[0] -= 100
            
                # once either play wins or there is a draw, game over both players are done
                self.dones = {i: True for i in range(self.num_agents)}

        else:
            # invalid move, some sort of negative reward
            self.rewards[self.agent_selection] = -10

        # Switch selection to next agents
        self.agent_selection = self._agent_selector.next()

        if observe:
            return self.observe(self.agent_selection)
        else:
            return

    def reset(self, observe=True):
        # reset environment
        self.board = Board()

        self.rewards = {i: 0 for i in range(self.num_agents)}
        self.dones = {i: False for i in range(self.num_agents)}
        self.infos = {i: {'legal_moves': [1] * 9} for i in range(self.num_agents)}

        # selects the first agent
        self._agent_selector.reinit(self.agent_order)
        self.agent_selection = self._agent_selector.next()
        if observe:
            return self.observe(self.agent_selection)
        else:
            return

    def render(self, mode='human'):
        print("Board: " + str([square.state for square in self.board.squares]))

    def close(self):
        pass
