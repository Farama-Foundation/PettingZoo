class Agent:
    def __new__(cls, *args, **kwargs):
        agent = super().__new__(cls)
        return agent

    @property
    def observation_space(self):
        raise NotImplementedError()

    @property
    def action_space(self):
        raise NotImplementedError()

    def __str__(self):
        return f"<{type(self).__name__} instance>"
