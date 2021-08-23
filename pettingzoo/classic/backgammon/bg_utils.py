def get_valid_actions(env, roll):
    a = env.game.get_valid_plays(env.colors[env.agent_selection], roll)
    return a


def to_bar(action, roll):
    if action == 25:  # bar
        if roll < 0:  # white
            return ('bar', 24 - abs(roll))
        else:  # black
            return ('bar', abs(roll) - 1)
    else:
        if action + roll - 1 > 23:
            return (action - 1, 24)
        elif action + roll - 1 < 0:
            return (action - 1, -1)
        else:
            return (action - 1, action + roll - 1)


def from_bar(action):
    bears_off = False
    if action[1] == -1 or action[1] == 24:
        bears_off = True
    if action[0] == 'bar':
        if action[1] > 12:  # white, top
            return (25, -(24 - action[1]), bears_off)
        else:  # black, bottom
            return (25, (action[1] + 1), bears_off)
    else:
        return (action[0] + 1, action[1] - action[0], bears_off)


# action goes from single number to a tuple
def to_bg_format(action, roll):
    base = 26
    low_roll = min(roll)
    high_roll = max(roll)

    if action == base**2 * 2:
        return (())

    if action < base**2:  # Low roll first
        dig1 = action % base
        dig2 = action // base
        a = to_bar(dig1, low_roll)
        b = to_bar(dig2, high_roll)
        if b[0] != 'bar' and b[0] > -1:
            return (a, b)
        else:
            return (a,)

    else:  # High roll first
        action = action - base**2
        dig1 = action % base
        dig2 = action // base
        a = to_bar(dig1, high_roll)
        b = to_bar(dig2, low_roll)
        if b[0] != 'bar' and b[0] > -1:
            return (a, b)
        else:
            return (a,)


# takes list of tuples and converts to a discrete value
def to_gym_format(actions, roll):
    high_roll = max(roll)
    low_roll = min(roll)
    nums = []
    base = 26
    for act in actions:
        if len(act) == 1:
            a, diff1, bears_off = from_bar(act[0])
            if bears_off:
                diff1 = high_roll if abs(diff1) > abs(low_roll) else low_roll
            if abs(diff1) == abs(high_roll):  # high first
                a += base**2
            nums.append(a)
        elif isinstance(act[0], int) or act[0] == 'bar':
            a, diff1, bears_off = from_bar(act)
            if bears_off:
                diff1 = high_roll if abs(diff1) > abs(low_roll) else low_roll
            if abs(diff1) == abs(high_roll):  # high first
                a += base**2
            nums.append(a)
        elif len(act) == 2:
            a, diff1, bears_off1 = from_bar(act[0])
            b, diff2, bears_off2 = from_bar(act[1])
            if bears_off1 or bears_off2:
                if bears_off1 and not bears_off2:
                    if abs(diff2) == abs(high_roll):
                        diff1 = low_roll
                    else:
                        diff1 = high_roll
                elif not bears_off1 and bears_off2:
                    if abs(diff1) == abs(high_roll):
                        diff2 = low_roll
                    else:
                        diff2 = high_roll
            num = a + base * b
            if diff1 > diff2:  # high first
                num += base**2
            nums.append(num)
    return nums


def double_roll(moves):
    out = []
    for move in moves:
        if len(move) > 1:
            out.append((move[0], move[1]))
        else:
            out.append(move[0])
    return out


def opp_agent(env, agent):
    return env.agents[0] if agent == env.agents[1] else env.agents[1]


def valid_action(env, action):
    return env.action_spaces[env.agent_selection].contains(action)
