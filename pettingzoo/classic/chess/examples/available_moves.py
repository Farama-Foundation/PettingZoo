import gym
import gym_chess
from pprint import pprint

env = gym.make('ChessVsRandomBot-v0')

def available_moves():
	state = env.state
	moves_p1 = env.get_possible_moves(state, 1)
	moves_p2 = env.get_possible_moves(state, -1)
	pprint(moves_p1)
	pprint(moves_p2)

	# no actions left -> resign
	if len(moves_p1) == 0:
		print('resigning is the only move...')
		resign_action = env.resign()

	# chess coordinates Player 1
	for m in moves_p1:
		print(env.convert_coords(m))

	# chess coordinates Player 2
	for m in moves_p2:
		print(env.convert_coords(m))

	# Player 1 moves
	for piece in set([m['piece_id'] for m in moves_p1]):
		env.render_moves(state, piece, moves_p1, mode='human')

	# Player 2 moves
	for piece in set([m['piece_id'] for m in moves_p2]):
		env.render_moves(state, piece, moves_p2, mode='human')


if __name__ == "__main__":
	available_moves()