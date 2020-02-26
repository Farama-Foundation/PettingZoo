class agent_selection():
    '''
        Outputs an agent in the given order whenever agent_select is called. Can reinitialize to a new order
    '''
    def __init__(self, agent_order):
        self.reinit(agent_order)
    
    def reinit(self, agent_order):
        self.agent_order = agent_order
        self._current_agent = 0
    
    @property
    def agent_select(self):
        self._current_agent = (self._current_agent + 1) % len(self.agent_order)
        return self.agent_order[self._current_agent - 1]
                
# env = agent_selection([10,20,30,40])
# for i in range(10):
#     print(env.agent_select)
#     if i == 4:
#         env.reinit([11,21,31,41])
    