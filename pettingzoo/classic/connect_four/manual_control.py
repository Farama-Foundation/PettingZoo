def manual_control(**kwargs):
    from .connect_four import env as _env
    env = _env(**kwargs)

    done = all(env.dones.values())

    print("valid actions are column indices from 0 - 6")
    while not done:
        current_player = env.agent_selection + 1

        action = int(input(f"Player {current_player}: "))

        # check if its a valid action
        if env.board[action] == 0:
            obs = env.step(action)
            print(obs)

            done = all(env.dones.values())

            if done:
                print(f"Player {current_player} won!")
                break
        else:
            print("Invalid move")
