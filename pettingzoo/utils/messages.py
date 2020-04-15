
step_before_reset = "reset() needs to be called before step"
observe_before_reset = "reset() needs to be called before observe"


def action_warning(action_space, action):
    return "action must be in the env.action_spaces[env.agent_selection]. Action space is: {}, Action is: {}".format(action_space, action)
