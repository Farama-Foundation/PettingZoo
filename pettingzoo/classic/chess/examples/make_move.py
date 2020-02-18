import gym
import gym_chess

env = gym.make('ChessVsRandomBot-v0')

def make_move():
	state = env.state
	player = 1
	actions = env.get_possible_actions(state, player)
	print(actions)
	for a in actions:
		print(env.action_to_move(a, player))

	for a in actions:
		state, reward, done, __ = env.step(a)
		__ = env.reset()


if __name__ == "__main__":
	make_move()
