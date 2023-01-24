import numpy as np
from board import Board

board = Board()

board.print_pieces()

print("--- TESTING board.check_for_winner() ---\n")
print("Flattened board (default):", board) # flattened

print("Below boards are 3x9 for easier debugging, would be flattened in real cases")

print("\nplayer_1 win horizontal: ")
board.squares = np.array([[ 1., -1.,  2.,  0.,  0.,  0.,  0.,  0.,  0.],
                          [ 0.,  3., -3.,  0.,  0.,  0.,  0.,  0.,  0.],
                          [ 0.,  0.,  3.,  0.,  0.,  0.,  0.,  0.,  0.]]).flatten()
print(board.squares.reshape(3, 3, 3))
print("TOP PIECES: \n", board.get_flatboard().reshape(3,3))
print("Winner: ", board.check_for_winner())
board.print_pieces()


print("\nNo winner example: ")
board.squares = np.array([[ 1., -1.,  2.,  0.,  0.,  0.,  0.,  0.,  0.],
                          [ 0.,  3., -3.,  0.,  0.,  0.,  0.,  0.,  0.],
                          [ 0.,  0., 0.,  0.,  0.,  0.,  0.,  0.,  0.]]).flatten()
print(board.squares.reshape(3, 3,3 ))
print("TOP PIECES: \n", board.get_flatboard().reshape(3,3))
print("Winner: ", board.check_for_winner())
board.print_pieces()


print("\nplayer_2 (-1) win horizontal: ")
board.squares = np.array([[ -1., -1.,  -2.,  0.,  0.,  0.,  0.,  0.,  0.],
                          [ 0.,   3.,   4.,  0.,  0.,  0.,  0.,  0.,  0.],
                          [ 0.,  -5,   -6.,  0.,  0.,  0.,  0.,  0.,  0.]]).flatten()
print(board.squares.reshape(3, 3, 3))
print("TOP PIECES: \n", board.get_flatboard().reshape(3,3))
print("Winner: ", board.check_for_winner())
board.print_pieces()


print("\nplayer_2 (-1) win vertical: ")
board.squares = np.array([[ -1., -1.,  -2.,  0.,  0.,  0.,  0.,  0.,  0.],
                          [ 0.,   0.,   3.,  0.,  0.,  0.,  0.,  0.,  0.],
                          [ 0.,  0.,   0.,  -5.,  0.,  0.,  -6.,  0.,  0.]]).flatten()
print(board.squares.reshape(3, 3, 3))
print("TOP PIECES: \n", board.get_flatboard().reshape(3,3))
print("Winner: ", board.check_for_winner())
board.print_pieces()


print("\nplayer_2 (-1) win diagonal: ")
board.squares = np.array([[ -1., -1.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
                          [ 0.,   0.,   -2,  0.,  0.,  0.,  0.,  0.,  0.],
                          [ 0.,  0.,   5.,  0.,  -5.,  0.,  0.,  0.,  -6.]]).flatten()
print(board.squares.reshape(3, 3, 3))
print("TOP PIECES: \n", board.get_flatboard().reshape(3,3))
print("Winner: ", board.check_for_winner())
board.print_pieces()

print("\nplayer_2 (-1) win diagonal: ")
board.squares = np.array([[ -1., -1.,  -2.,  0.,  0.,  0.,  0.,  0.,  0.],
                          [ 0.,   0.,   2.,  0.,  -3.,  0.,  0.,  0.,  0.],
                          [ 0.,  0.,   0.,  0.,  0.,  0.,  0.,  0.,  -6.]]).flatten()
print(board.squares.reshape(3, 3, 3))
print("TOP PIECES: \n", board.get_flatboard().reshape(3,3))
print("Winner: ", board.check_for_winner())
board.print_pieces()

print("--- TESTING board.check_for_winner() ---\n")

print("\nNo winner example: ")
board.squares = np.array([[ 1., -1.,  2.,  0.,  0.,  0.,  0.,  0.,  0.],
                          [ 0.,  3., -3.,  0.,  0.,  0.,  0.,  0.,  0.],
                          [ 0.,  0., 0.,  0.,  0.,  0.,  0.,  0.,  0.]]).flatten()
print(board.squares.reshape(3, 3, 3))
print("TOP PIECES: \n", board.get_flatboard().reshape(3,3))
print("Winner: ", board.check_for_winner())
board.print_pieces()

action = board.get_action(pos=8, piece=6)  # 35
agent = 0
print("\n--- NEXT TURN: action", action)
board.play_turn(agent, action)

print(board.squares.reshape(3, 3,3 ))
print("\nTOP PIECES: \n", board.get_flatboard().reshape(3,3))
print("Winner: ", board.check_for_winner())
board.print_pieces()

action = board.get_action(pos=8, piece=6)  # Second large piece in bottom right corner
agent = 0
print("\n--- NEXT TURN: action", action)
board.play_turn(agent, action)

print(board.squares.reshape(3, 3,3 ))
print("\nTOP PIECES: \n", board.get_flatboard().reshape(3,3))
print("Winner: ", board.check_for_winner())
board.print_pieces()

action = board.get_action(pos=8, piece=5)  # First large piece in bottom middle
agent = 0
print("\n--- NEXT TURN: action", action)
board.play_turn(agent, action)

print(board.squares.reshape(3, 3,3 ))
print("\nTOP PIECES: \n", board.get_flatboard().reshape(3,3))
print("Winner: ", board.check_for_winner())
board.print_pieces()

action = board.get_action(pos=7, piece=5)  # First large piece move to bottom left corner
agent = 0
print("\n--- NEXT TURN: action", action)
board.play_turn(agent, action)

print(board.squares.reshape(3, 3,3 ))
print("\nTOP PIECES: \n", board.get_flatboard().reshape(3,3))
print("Winner: ", board.check_for_winner())
board.print_pieces()

action = board.get_action(pos=7, piece=4)  # Second medium piece move to bottom middle
agent = 0
print("\n--- NEXT TURN: action", action)
board.play_turn(agent, action)

print(board.squares.reshape(3, 3, 3))
print("\nTOP PIECES: \n", board.get_flatboard().reshape(3,3))
print("Winner: ", board.check_for_winner())
board.print_pieces()

print("-- TESTING FROM BLANK BOARD -- ")
board = Board()
board.print_pieces()

action = board.get_action(pos=8, piece=6)
agent = 0
print("\n--- NEXT TURN: action", action)
board.play_turn(agent, action)

print(board.squares.reshape(3, 3, 3))
print("\nTOP PIECES: \n", board.get_flatboard().reshape(3,3))
print("Winner: ", board.check_for_winner())
board.print_pieces()
