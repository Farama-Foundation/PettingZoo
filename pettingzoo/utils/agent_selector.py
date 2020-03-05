class agent_selector():
    '''
        Outputs an agent in the given order whenever agent_select is called. Can reinitialize to a new order
    '''
    def __init__(self, agent_order):
        self.reinit(agent_order)

    def reinit(self, agent_order):
        self.agent_order = agent_order
        self._current_agent = 0

    def next(self):
        self._current_agent = (self._current_agent + 1) % len(self.agent_order)
        return self.agent_order[self._current_agent - 1]

    def is_last(self):
        '''
        Does not work as expected if you change the order
        '''
        return self._current_agent == self.agent_order[-1]
    
    # def peek_next_agent(self):
    #     return self.agent_order[self._current_agent]
                
# env = agent_selection([10,20,30,40])
# for i in range(10):
#     print("curr", env.agent_select)
#     # print("next", env.peek_next_agent())
#     if i == 4:
#         env.reinit([11,21,31,41])
