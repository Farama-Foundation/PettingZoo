import os
import sys
# import time

from copy import copy
from six import StringIO
from pprint import pprint

import gym
from gym import spaces, error, utils
from gym.utils import seeding
import numpy as np


uniDict = {
	'p': "♙", 'r': "♖", 'n': "♘", 'b': "♗", 'k': "♔", 'q': "♕", 
	'P': "♟", 'R': "♜", 'N': "♞", 'B': "♝", 'K': "♚", 'Q': "♛" ,
	'.': '.'
}

pieces_to_ids = {
	'R1': 1, 'N1': 2, 'B1': 3, 'Q': 4, 'K': 5, 'B2': 6, 'N2': 7, 'R2': 8,
	'P1': 9, 'P2': 10, 'P3': 11, 'P4': 12, 'P5': 13, 'P6': 14, 'P7': 15, 'P8': 16, 
	'r1': -1, 'n1': -2, 'b1': -3, 'q': -4, 'k': -5, 'b2': -6, 'n2': -7, 'r2': -8,
	'p1': -9, 'p2': -10, 'p3': -11, 'p4': -12, 'p5': -13, 'p6': -14, 'p7': -15, 'p8': -16, 
	'.': 0
}

# return sign of number
sign = lambda x: (1, -1)[x < 0]

""" 
    AGENT POLICY 
    ------------ 
"""
def make_random_policy(np_random):
	def random_policy(state):
		opp_player = -1
		moves = ChessEnv.get_possible_moves(state, opp_player)
		# No moves left
		if len(moves) == 0:
			return 'resign'
		else:
			return np.random.choice(moves)
	return random_policy


""" 
    CHESS GYM ENVIRONMENT CLASS
    --------------------------- 
"""

class ChessEnv(gym.Env):

	pieces_values = {'p': 1, 'r': 5, 'n': 3, 'b': 3, 'k': None, 'q': 10, '.': 0}
	ids_to_pieces = {v: k for k, v in pieces_to_ids.items()}
	WHITE = 1
	BLACK = -1
	CASTLE_MOVE_ID = 20
	KING_CATSLE = 1
	QUEEN_CATSLE = 2
	#metadata = {'render.modes': ['human']}

	def __init__(self, player_color=1, opponent="random", log=True):
		self.moves_max = 149
		self.log = log
		
		# One action (for each board position) x (no. of pieces), 2xcastles, offer/accept draw and resign
		self.observation_space = spaces.Box(-16,16, (8,8)) # board 8x8
		self.action_space = spaces.Discrete(64*16 + 4)

		self.player = player_color # define player # TODO: implement
		self.opponent = opponent # define opponent

		# reset and build state
		self._seed()
		self._reset()


	def _seed(self, seed=None):
		self.np_random, seed = seeding.np_random(seed)

		# Update the random policy if needed
		if isinstance(self.opponent, str):
			if self.opponent == 'random':
				self.opponent_policy = make_random_policy(self.np_random)
			elif self.opponent == 'none':
				self.opponent_policy = None
			else:
				raise error.Error('Unrecognized opponent policy {}'.format(self.opponent))
		else:
			self.opponent_policy = self.opponent

		return [seed]


	def _step(self, action):
		"""
		Run one timestep of the environment's dynamics. When end of episode
		is reached, reset() should be called to reset the environment's internal state.

		Input
		-----
		action : an action provided by the environment

		Outputs
		-------
		(observation, reward, done, info)
		observation : agent's observation of the current environment
		reward [Float] : amount of reward due to the previous action
		done : a boolean, indicating whether the episode has ended
		info : a dictionary containing other diagnostic information from the previous action
		"""
		# validate action
		assert self.action_space.contains(action), "ACTION ERROR {}".format(action)

		# Game is done
		if self.done:
			return self.state, 0., True, {'state': self.state}
		if self.state['on_move'] > self.moves_max:
			return self.state, 0., True, {'state': self.state}

		# make move
		self.state, reward, self.done = self.player_move(
			self.current_player, self.state, action, 
			render=self.log, render_msg='Player '+str(self.current_player))

		if self.done:
			return self.state, reward, self.done, {'state': self.state}

		# player vs. player game
		if not self.opponent_policy:
			# +1 step
			if self.current_player == -1:
				self.state['on_move'] += 1
			self.current_player *= -1
			return self.state, reward, self.done, {'state': self.state}

		# Bot Opponent play
		#
		else:
			opp_move = self.opponent_policy(self.state)
			opp_action = ChessEnv.move_to_actions(opp_move)

			# make move
			self.state, opp_reward, self.done = self.player_move(
				-1, self.state, opp_action, 
				render=self.log, render_msg='Opponent')

			total_reward = reward - opp_reward
			self.state['on_move'] += 1
			return self.state, total_reward, self.done, {'state': self.state}


	def player_move(self, player, state, action, render=False, render_msg='Player'):
		"""
		Returns (state, reward, done) 
		"""
		#Resign
		if ChessEnv.has_resigned(action):
			return state, -100, True
		#Play
		move = ChessEnv.action_to_move(action, player)
		new_state, prev_piece, reward = ChessEnv.next_state(
			copy(state), move, player)
		#Keep track of movements
		piece_id = move['piece_id']
		if abs(piece_id) == ChessEnv.CASTLE_MOVE_ID:
			new_state['kr_moves'][player*5] += 1
		else:
			new_state['kr_moves'][piece_id] += 1
		#Save material captured
		if prev_piece != 0:
			new_state['captured'][player].append(prev_piece)
		#Save current state and keep track of repetitions 
		self.saved_states = ChessEnv.encode_current_state(state, self.saved_states)
		self.repetitions = max([v for k, v in self.saved_states.items()])

		#3-fold repetition => DRAW
		if self.repetitions >= 3:
			return new_state, 0, True
		###Render
		if render: 
			ChessEnv.render_moves(state, move['piece_id'], [move], mode='human')
			print(' '*10, '>'*10, render_msg)
			# self._render()
		return new_state, reward, False


	def _reset(self):
		"""
		Resets the state of the environment, returning an initial observation.
		Outputs -> observation : the initial observation of the space. (Initial reward is assumed to be 0.)
		"""
		# reset pieces (pawns that became queen become pawns again)
		ChessEnv.ids_to_pieces = {v: k for k, v in pieces_to_ids.items()}
		# vars
		self.state = {}
		self.done = False
		self.current_player = 1
		self.saved_states = {}
		self.repetitions = 0     # 3 repetitions ==> DRAW
		# register king's and rooks' (and all other pieces) moves
		pieces = np.linspace(1, 16, 16, dtype=int)
		self.state['kr_moves'] = {**{p: 0 for p in pieces}, **{-p: 0 for p in pieces}} 
		# material captured
		self.state['captured'] = {1: [], -1: []}
		# current move
		self.state['on_move'] = 1

		# Board
		board = [['R1', '.', '.', 'K', '.', '.', '.', 'R2']]
		board += [['P1', '.', '.', '.', '.', '.', '.', 'P8']]
		board += [['.']*8] * 4
		board += [['p1', '.', '.', '.', '.', '.', '.', 'p8']]
		board += [['r1', '.', '.', 'k', '.', '.', '.', 'r2']]
		self.state['board'] = np.array([[pieces_to_ids[x] for x in row] for row in board])
		self.state['prev_board'] = copy(self.state['board'])
		return self.state

		# TODO
		#
		# Let the opponent play if it's not the agent's turn
		# if self.player_color != self.to_play:
		#     a = self.opponent_policy(self.state)
		#     HexEnv.make_move(self.state, a, HexEnv.BLACK)
		#     self.to_play = HexEnv.WHITE


	def _render(self, mode='human', close=False):
		return ChessEnv.render_board(self.state, mode=mode, close=close)

	@staticmethod
	def render_board(state, mode='human', close=False):
		"""
		Render the playing board
		"""
		board = state['board']
		outfile = StringIO() if mode == 'ansi' else sys.stdout

		outfile.write('    ')
		outfile.write('-' * 25)
		outfile.write('\n')

		for i in range(7,-1,-1):
			outfile.write(' {} | '.format(i+1))
			for j in range(7,-1,-1):
				piece = ChessEnv.ids_to_pieces[board[i,j]]
				figure = uniDict[piece[0]]
				outfile.write(' {} '.format(figure))
			outfile.write('|\n')
		outfile.write('    ')
		outfile.write('-' * 25)
		outfile.write('\n      a  b  c  d  e  f  g  h ')
		outfile.write('\n')
		outfile.write('\n')

		if mode != 'human':
			return outfile


	@staticmethod
	def render_moves(state, piece_id, moves, mode='human'):
		"""
		Render the possible moves that a piece can take
		"""
		board = state['board']
		moves_pos = [m['new_pos'] for m in moves if m['piece_id']==piece_id]

		outfile = StringIO() if mode == 'ansi' else sys.stdout
		outfile.write('    ')
		outfile.write('-' * 25)
		outfile.write('\n')

		for i in range(7,-1,-1):
			outfile.write(' {} | '.format(i+1))
			for j in range(7,-1,-1):
				piece = ChessEnv.ids_to_pieces[board[i,j]]
				figure = uniDict[piece[0]]

				# check moves + piece
				if board[i,j] == piece_id:
					outfile.write('<{}>'.format(figure))
				elif moves_pos and any(np.equal(moves_pos,[i,j]).all(1)):
					if piece == '.':
						if piece_id == ChessEnv.CASTLE_MOVE_ID:
							outfile.write('0-0')
						else:
							outfile.write(' X ')
					else:
						outfile.write('+{}+'.format(figure))
				else:
					outfile.write(' {} '.format(figure))
			outfile.write('|\n')
		outfile.write('    ')
		outfile.write('-' * 25)
		outfile.write('\n      a  b  c  d  e  f  g  h ')
		outfile.write('\n')
		outfile.write('\n')

		if mode != 'human':
			return outfile

	@staticmethod
	def encode_current_state(state, saved_states):
		board = state['board']
		kr_moves = state['kr_moves']
		castle_p1 = int(sum([k for k in kr_moves if k in [1,5,8]]) == 0)
		castle_p2 = int(sum([k for k in kr_moves if k in [-1,-5,-8]]) == 0)
		new_saved_states = copy(saved_states)
		pieces_encoding = { '.': 0, 'p': 1, 'b': 2, 'n': 3, 'r': 4, 'k': 5, 'q': 6 }
		encoding = str(castle_p1) + str(castle_p2)
		for i in range(8):
			for j in range(8):
				piece_id = board[i][j]
				player = sign(piece_id)
				piece_type = ChessEnv.ids_to_pieces[piece_id][0].lower()
				piece_encode = pieces_encoding[piece_type]
				if piece_encode != 0:
					piece_encode += 3*(1-player)
				# hex encoding
				encoding += hex(piece_encode)[2:]
		if encoding in new_saved_states:
			new_saved_states[encoding] += 1
		else:
			new_saved_states[encoding] = 1
		return new_saved_states

	@staticmethod
	def resign_action():
		return 8**2 * 16 + 3
	@staticmethod
	def has_resigned(action):
		return action == ChessEnv.resign_action()

	@staticmethod
	def is_a_draw(state):
		return (state.repetitions >= 3)

	# @staticmethod
	# def offer_draw_action():
	# 	return 8**2 * 16 + 4
	# @staticmethod
	# def draw_offered(action, ):
	# 	return action == ChessEnv.offer_draw_action()

	# @staticmethod
	# def accept_draw_action():
	# 	return 8**2 * 16 + 5
	# @staticmethod
	# def draw_accepted():
	# 	return action == ChessEnv.accept_draw_action()

	@staticmethod
	def castle_move_to_action(castle_type):
		return 8**2 * 16 + abs(castle_type)

	@staticmethod
	def move_to_actions(move):
		"""
		Encode move into action
		"""
		if move == 'resign':
			return ChessEnv.resign_action()
		elif move['type'] == 'castling':
			return ChessEnv.castle_move_to_action(move['castle'])
		else:
			piece_id = move['piece_id']
			new_pos = move['new_pos']
			return 64*(abs(piece_id) - 1) + (new_pos[0]*8 + new_pos[1]).item()

	@staticmethod
	def action_to_move(action, player):
		"""
		Decode move from action
		"""
		t = 8**2 * 16
		castles_pos = {
			1: { 
				ChessEnv.KING_CATSLE: [0, 1],
				ChessEnv.QUEEN_CATSLE: [0, 5],
			},
			-1: {
				ChessEnv.KING_CATSLE: [7, 1],
				ChessEnv.QUEEN_CATSLE: [7, 5],
			}
		}

		if action in [t+1, t+2]: # castling
			castle_type = action - (8**2 * 16)
			new_pos = castles_pos[player][castle_type]
			return {
				'piece_id': player * ChessEnv.CASTLE_MOVE_ID,
				'pos': None,
				'new_pos': new_pos,
				'type': 'castling',
				'castle': castle_type
			}
		else:
			square = action % 64 
			column = square % 8
			row = (square - column) // 8
			piece_id = (action - square) // 64 + 1
			return {
				'piece_id': piece_id * player,
				'new_pos': np.array([int(row), int(column)]),
			}

	@staticmethod
	def next_state(state, move, player):
		"""
		Return the next state given a move
		-------
		(next_state, previous_piece, reward)
		"""
		new_state = copy(state)
		new_state['prev_board'] = copy(state['board'])

		board = copy(new_state['board'])
		new_pos = move['new_pos']
		piece_id = move['piece_id']
		reward = 0

		# check for castle
		# TODO
		if piece_id == player * ChessEnv.CASTLE_MOVE_ID:
			return ChessEnv.castle_action_to_state(
						state, player, move['castle']), 0, 0

		# find old position 
		try:
			old_pos = np.array([x[0] for x in np.where(board == piece_id)])
		except:
			print('piece_id', piece_id)
			print(board)
			raise Exception()
		r, c = old_pos[0], old_pos[1]
		board[r, c] = 0

		# replace new position
		new_pos = np.array(new_pos) 
		r, c = new_pos
		prev_piece = board[r, c]
		board[r, c] = piece_id

		# Reward for capturing a piece 
		piece_type = ChessEnv.ids_to_pieces[prev_piece][0].lower()
		reward += ChessEnv.pieces_values[piece_type]

		# check for pawn becoming a queen
		if ChessEnv.ids_to_pieces[piece_id][0].lower() == 'p':
			if (player == 1 and new_pos[0] == 7):
				ChessEnv.ids_to_pieces[piece_id] = 'Q'
				reward += 10
				# print(' '*40, '!! ==> Player', player, 'pawn became a Queen <== !!', end='')
			elif (player == -1 and new_pos[0] == 0):
				ChessEnv.ids_to_pieces[piece_id] = 'q'
				reward += 10
				# print(' '*40, '!! ==> Player', player, 'pawn became a Queen <== !!', end='')

		new_state['board'] = board
		return new_state, prev_piece, reward


	@staticmethod
	def castle_action_to_state(state, player, castle_move):
		board = copy(state['board'])
		kr_moves = state['kr_moves']
		assert kr_moves[5*player] == 0, "Castling move error - king has already moved"
		king_pos = np.where(board == player*5)
		king_x, king_y = king_pos[0][0], king_pos[1][0]

		# make castling move
		if castle_move == ChessEnv.KING_CATSLE:
			assert kr_moves[1*player] == 0, "Castling move error - rook has already moved"
			board[king_x, king_y-1] = player*1
			board[king_x, king_y-2] = player*5
			board[king_x, king_y] = 0
			board[king_x, 0] = 0
		elif castle_move == ChessEnv.QUEEN_CATSLE:
			assert kr_moves[8*player] == 0, "Castling move error - rook has already moved"
			board[king_x, king_y+1] = player*8
			board[king_x, king_y+2] = player*5
			board[king_x, king_y] = 0
			board[king_x, 7] = 0
		else:
			raise Exception("ERROR - NON-EXISTENT CASTLING MOVE") 

		new_state = copy(state)
		new_state['board'] = board
		return new_state


	@staticmethod
	def get_possible_actions(state, player):
		moves = ChessEnv.get_possible_moves(state, player)
		return [ChessEnv.move_to_actions(m) for m in moves]

	@staticmethod
	def get_possible_moves(state, player, attack=False):
		"""
		Returns a list of numpy tuples
		-----
		piece_id - id
		position - (row, ccolumn)
		new_position - (row, column)
		"""
		board = state['board']
		total_moves = []

		for position, piece_id in np.ndenumerate(board):
			if piece_id != 0 and sign(piece_id) == sign(player):

				piece_name = ChessEnv.ids_to_pieces[piece_id]
				piece_type = piece_name[0].lower()
				#assert piece_type in ['k', 'q', 'r', 'b', 'n', 'p', '.'], "ERROR - inexistent piece type"

				if piece_type == 'k':
					moves = ChessEnv.king_actions(state, position, player, attack=attack)
				elif piece_type == 'q':
					moves = ChessEnv.queen_actions(state, position, player, attack=attack)
				elif piece_type == 'r':
					moves = ChessEnv.rook_actions(state, position, player, attack=attack)
				elif piece_type == 'b':
					moves = ChessEnv.bishop_actions(state, position, player, attack=attack)
				elif piece_type == 'n':
					moves = ChessEnv.knight_actions(state, position, player, attack=attack)
				elif piece_type == 'p':
					moves = ChessEnv.pawn_actions(state, position, player, attack=attack)
				elif piece_type == '.':
					moves = []
					continue
				else:
					raise Exception("ERROR - inexistent piece type ") 

				# formatting
				for m in moves:
					total_moves.append({
							'piece_id': piece_id,
							'pos': position,
							'new_pos': m,
							'type': 'move'
						})
			else: 
				continue

		# TODO: add castling
		if not attack: 
			castle_moves = ChessEnv.castle_moves(state, player)
			if castle_moves:
				for k, v in castle_moves.items():
					total_moves.append({
								'piece_id': player * ChessEnv.CASTLE_MOVE_ID,
								'pos': None,
								'new_pos': v,
								'type': 'castling',
								'castle': k
							})

				# print('===============> We got some castling moves !!!')
				# print('player', player)
				# print(castle_moves)

		# Check if the king is checked
		if not attack and ChessEnv.king_is_checked(state, player):
			# print('\n!! ==> Player ', player,' king is checked <== !!')
			def no_check_next_state(state, move, player):
				next_state, __, __ = ChessEnv.next_state(state, move, player)
				return not ChessEnv.king_is_checked(next_state, player)
			return [m for m in total_moves if no_check_next_state(state, m, player)]
		else:
			return total_moves


	@staticmethod 
	def king_actions(state, position, player, attack=False):
		"""
		KING ACTIONS
		------------
		"""
		go_to = []
		board = state['board']
		kr_moves = state['kr_moves']
		pos = np.array(position)
		steps = [[1,0],[-1,0],[0,1],[0,-1],[1,1],[1,-1],[-1,1],[-1,-1]]

		for step in steps:
			move = pos + np.array(step)
			if attack:
				if ChessEnv.king_attack(state, move, player):
					go_to.append(move)
			else:
				if ChessEnv.king_move(state, move, player):
					go_to.append(move)
		return go_to

	@staticmethod
	def castle_moves(state, player):
		"""
		CASTLE ACTIONS
		----
		"""
		# TODO
		board = state['board']
		kr_moves = state['kr_moves']
		go_to = {}

		# print(kr_moves[5*player], kr_moves[1*player], kr_moves[8*player])

		if kr_moves[5*player] != 0:
			return {}

		# queen side
		def queen_side_castle(board, kr_moves, player):
			if kr_moves[8*player] != 0:
				return {}
			else:
				king_pos = np.where(board == player*5)
				king_x, king_y = king_pos[0][0], king_pos[1][0]
				pos1 = [king_x, king_y+1]
				pos2 = [king_x, king_y+2]

				for p in [pos1, pos2]:
					if board[p[0], p[1]] != 0:
						return {}

				sq_attacked = ChessEnv.squares_attacked(state, player)
				for p in [pos1, pos2]:
					if ChessEnv.move_in_list(p, sq_attacked):
						return {}

				return {ChessEnv.QUEEN_CATSLE: pos2}

		# king side
		def king_side_castle(board, kr_moves, player):
			if kr_moves[1*player] != 0:
				return {}
			else:
				king_pos = np.where(board == player*5)
				king_x, king_y = king_pos[0][0], king_pos[1][0]
				pos1 = [king_x, king_y-1]
				pos2 = [king_x, king_y-2]

				for p in [pos1, pos2]:
					if board[p[0], p[1]] != 0:
						return {}

				sq_attacked = ChessEnv.squares_attacked(state, player)
				for p in [pos1, pos2]:
					if ChessEnv.move_in_list(p, sq_attacked):
						return {}

				return {ChessEnv.KING_CATSLE: pos2}

		go_to = { **go_to, **queen_side_castle(board, kr_moves, player)}
		go_to = { **go_to, **king_side_castle(board, kr_moves, player)}
		return go_to


	@staticmethod 
	def queen_actions(state, position, player, attack=False):
		"""
		QUEEN ACTIONS
		-------------
		"""
		go_to = ChessEnv.rook_actions(state, position, player, attack=attack)
		go_to += ChessEnv.bishop_actions(state, position, player, attack=attack)
		return go_to


	@staticmethod 
	def rook_actions(state, position, player, attack=False):
		"""
		ROOK ACTIONS
		------------
		"""
		pos = np.array(position)
		go_to = []
		
		for i in [-1, +1]:
			step = np.array([i, 0])
			go_to += ChessEnv.iterative_steps(state, player, pos, step, attack=attack)

		for j in [-1, +1]:
			step = np.array([0, j])
			go_to += ChessEnv.iterative_steps(state, player, pos, step, attack=attack)

		return go_to


	@staticmethod 
	def bishop_actions(state, position, player, attack=False):
		"""
		BISHOP ACTIONS
		--------------
		"""
		pos = np.array(position)
		go_to = []
		
		for i in [-1, +1]:
			for j in [-1, +1]:
				step = np.array([i, j])
				go_to += ChessEnv.iterative_steps(state, player, pos, step, attack=attack)
		return go_to


	@staticmethod
	def iterative_steps(state, player, position, step, attack=False):
		"""
		Used to calculate Bishop, Rook and Queen moves
		"""
		go_to = []
		pos = np.array(position)
		step = np.array(step)
		k = 1
		while True:
			move = pos + k*step
			if attack:
				add_bool, stop_bool = ChessEnv.attacking_move(state, move, player)
				if add_bool:
					go_to.append(move)
				if stop_bool:
					break
				else:
					k += 1
			else:
				add_bool, stop_bool = ChessEnv.playable_move(state, move, player)
				if add_bool:
					go_to.append(move)
				if stop_bool:
					break
				else:
					k += 1
		return go_to


	@staticmethod 
	def knight_actions(state, position, player, attack=False):
		"""
		KNIGHT ACTIONS
		--------------
		"""
		go_to = []
		pos = np.array(position)
		moves = [pos + np.array([v,h]) for v in [-2, +2] for h in [-1, +1]]
		moves += [pos + np.array([v,h]) for v in [-1, +1] for h in [-2, +2]]
		
		# filter:
		for m in moves:
			if attack:
				add_bool, __ = ChessEnv.attacking_move(state, m, player)
				if add_bool:
					go_to.append(m)
			else:
				add_bool, __ = ChessEnv.playable_move(state, m, player)
				if add_bool:
					go_to.append(m)
		return go_to


	@staticmethod 
	def pawn_actions(state, position, player, attack=False):
		"""
		PAWN ACTIONS
		------------
		"""
		board = state['board']
		pos = np.array(position)
		go_to = []

		attack_moves = [
			pos + np.array([1, -1])*player, 
			pos + np.array([1, +1])*player, 
		]

		step_1 = np.array([1, 0]) * player
		step_2 = np.array([2, 0]) * player

		if attack:
			return [m for m in attack_moves 
				if ChessEnv.pos_is_in_board(m) 
				and not ChessEnv.is_own_king(board, m, player)]

		else:
			# moves only to empty squares
			#
			if board[pos[0]+1*player, pos[1]] == 0:
				go_to.append(pos + step_1)

				if (pos[0] == 1 and player == 1) or (pos[0] == 6 and player == -1):
					if board[pos[0]+2*player, pos[1]] == 0:
						go_to.append(pos + step_2)

			# attacks only opponent's pieces
			# 
			for m in reversed(attack_moves):
				if not ChessEnv.pos_is_in_board(m):
					continue
				elif ChessEnv.is_own_piece(board, m, player):
					continue
				elif ChessEnv.is_opponent_king(board, m, player):
					continue
				elif ChessEnv.is_opponent_piece(board, m, player):
					go_to.append(m)
					attack_moves.pop()
					continue
				elif board[m[0], m[1]] == 0:
					continue
				else:
					raise Exception("ERROR - PAWN ATTACK MOVES")

			# En passant capture
			#
			if (pos[0] == 4 and player == 1) or (pos[0] == 3 and player == -1):
				prev_board = state['prev_board']
				for m in attack_moves:
					if not ChessEnv.pos_is_in_board(m):
						continue
					elif ChessEnv.is_own_piece(board, m, player):
						continue
					elif ChessEnv.is_opponent_king(board, m, player):
						continue
					else:
						col = m[1]
						row = pos[0]
						if player == 1:
							prev_row = 6
						else:
							prev_row = 1

						sq_before = prev_board[prev_row, col]
						sq_after = board[row, col]

						piece_before = ChessEnv.ids_to_pieces[sq_before]
						piece_after = ChessEnv.ids_to_pieces[sq_after]

						piece_type_before = piece_before[0].lower()
						piece_type_after = piece_after[0].lower()

						if piece_type_before == 'p' and piece_type_after == 'p':
							# print('='*40, 'En passant move detected !!!')
							# print(prev_board)
							# print(board)
							go_to.append(m)
							# ChessEnv.render_moves(state, board[pos[0], pos[1]], moves, mode=)
			return go_to


	@staticmethod
	def king_move(state, move, player):
		"""
		return squares to which the king can move, 
		i.e. unattacked squares that can be:
		- empty squares
		- opponent pieces (excluding king)
		If opponent king is encountered, then there's a problem...
		=> return [<bool> add_move]
		"""
		board = state['board']
		checked_squares = ChessEnv.squares_attacked(state, player)

		if not ChessEnv.pos_is_in_board(move):
			return False
		elif ChessEnv.move_in_list(move, checked_squares):
			return False
		elif ChessEnv.is_own_piece(board, move, player):
			return False
		elif ChessEnv.is_opponent_king(board, move, player):
			raise Exception('KINGS NEXT TO EACH OTHER ERROR \n{} \n{} \n{}'.format(
				board, move, player))
		elif ChessEnv.is_opponent_piece(board, move, player):
			return True
		elif board[move[0], move[1]] == 0: # empty square
			return True
		else:
			raise Exception('KING MOVEMENT ERROR \n{} \n{} \n{}'.format(
				board, move, player))

	@staticmethod
	def king_attack(state, move, player):
		"""
		return all the squares that the king can attack, except:
		- squares outside the board
		If opponent king is encountered, then there's a problem...
		=> return [<bool> add_move]
		"""
		board = state['board']
		if not ChessEnv.pos_is_in_board(move):
			return False
		elif ChessEnv.is_own_piece(board, move, player):
			return True
		elif ChessEnv.is_opponent_king(board, move, player):
			raise Exception('KINGS NEXT TO EACH OTHER ERROR \n{} \n{} \n{}'.format(
				board, move, player))
		elif ChessEnv.is_opponent_piece(board, move, player):
			return True
		elif board[move[0], move[1]] == 0: # empty square
			return True
		else:
			raise Exception('KING ATTACK ERROR \n{} \n{} \n{}'.format(
				board, move, player))


	@staticmethod
	def playable_move(state, move, player):
		"""
		return squares to which a piece can move
		- empty squares
		- opponent pieces (excluding king)
		=> return [<bool> add_move, <bool> break]
		"""
		board = state['board']
		if not ChessEnv.pos_is_in_board(move):
			return False, True
		elif ChessEnv.is_own_piece(board, move, player):
			return False, True
		elif ChessEnv.is_opponent_king(board, move, player):
			return False, True
		elif ChessEnv.is_opponent_piece(board, move, player):
			return True, True
		elif board[move[0], move[1]] == 0: # empty square
			return True, False
		else:
			raise Exception('MOVEMENT ERROR \n{} \n{} \n{}'.format(board, move, player))


	@staticmethod
	def attacking_move(state, move, player):
		"""
		return squares that are attacked or defended 
		- empty squares
		- opponent pieces (opponent king is ignored)
		- own pieces
		=> return [<bool> add_move, <bool> break]
		"""
		board = state['board']
		if not ChessEnv.pos_is_in_board(move):
			return False, True
		elif ChessEnv.is_own_piece(board, move, player):
			return True, True
		elif ChessEnv.is_opponent_king(board, move, player):
			return True, False
		elif ChessEnv.is_opponent_piece(board, move, player):
			return True, True
		elif board[move[0], move[1]] == 0: # empty square
			return True, False
		else:
			raise Exception('ATTACKING ERROR \n{} \n{} \n{}'.format(board, move, player))


	"""
	- flatten board
	- find move in movelist
	"""
	@staticmethod
	def move_in_list(move, move_list):
		move_list_flat = [ChessEnv.flatten_position(m) for m in move_list]
		move_flat = ChessEnv.flatten_position(move)
		return move_flat in move_list_flat
	@staticmethod
	def flatten_position(position):
		x, y = position[0], position[1]
		return x + y*8
	@staticmethod
	def boardise_position(position):
		x = position % 8
		y = (position - x)//8
		return x, y
 

	@staticmethod
	def pos_is_in_board(pos):
		return not (pos[0] < 0 or pos[0] > 7 or pos[1] < 0 or pos[1] > 7)

	@staticmethod 
	def squares_attacked(state, player):
		opponent_moves = ChessEnv.get_possible_moves(state, -player, attack=True)
		attacked_pos = [m['new_pos'] for m in opponent_moves]
		return attacked_pos

	@staticmethod 
	def king_is_checked(state, player):
		"""
		KING CHECK
		"""
		board = state['board']
		king_pos = np.where(board == player*5)
		king_pos = [king_pos[0][0], king_pos[1][0]]
		attacked_pos = ChessEnv.squares_attacked(state, player)
		return (any(np.equal(attacked_pos, king_pos).all(1)))

	@staticmethod 
	def king_is_mated(state, player):
		"""
		MATE
		"""
		return False


	"""
	Player Pieces
	"""
	@staticmethod 
	def is_own_piece(board, position, player):
		return ChessEnv.is_player_piece(board, position, player)
	@staticmethod 
	def is_opponent_piece(board, position, player):
		return ChessEnv.is_player_piece(board, position, -player)
	@staticmethod 
	def is_player_piece(board, position, player):
		x, y = position
		return  (board[x,y] != 0 and sign(board[x,y]) == player)


	"""
	Player Kings
	"""
	@staticmethod 
	def is_opponent_king(board, position, player):
		return ChessEnv.is_player_king(board, position, -player)
	@staticmethod 
	def is_own_king(board, position, player):
		return ChessEnv.is_player_king(board, position, player)
	@staticmethod 
	def is_player_king(board, position, player):
		v, h = position
		return (board[v, h] == player * 5)


	@staticmethod
	def convert_coords(move):
		"""
		TODO: include board context:
		- disambiguation
		- capture of opponent's piece marked with 'x'
		"""
		if move['type'] == 'castling':
			if move['castle'] == ChessEnv.KING_CATSLE:
				return '0-0'
			elif move['castle'] == ChessEnv.QUEEN_CATSLE:
				return '0-0-0'
			else:
				raise Exception('ERROR - wrong castling type')

		piece = ChessEnv.ids_to_pieces[move['piece_id']]
		old_pos = move['pos']
		new_pos = move['new_pos']
		alpha = 'abcdefgh'
		if piece[0].lower() != 'p':
			piece = piece[0].upper()
		else:
			piece = ''
		return '{}{}{}-{}{}'.format(piece, 
			alpha[old_pos[1]], old_pos[0]+1, 
			alpha[new_pos[1]], new_pos[0]+1)




