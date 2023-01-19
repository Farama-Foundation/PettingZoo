import numpy as np
from board import Board

board = Board()

board.print_pieces()

print("--- TESTING board.check_for_winner() ---\n")
print("Flattened board (default):", board) # flattened

print("Below boards are 3x9 for easier debugging, would be flattened in real cases")

print("\nplayer_1 win horizontal: ")
board.squares = np.array([[ 1., -1.,  1.,  0.,  0.,  0.,  0.,  0.,  0.],
                          [ 0.,  2., -2.,  0.,  0.,  0.,  0.,  0.,  0.],
                          [ 0.,  0.,  3.,  0.,  0.,  0.,  0.,  0.,  0.]]).flatten()
print(board.squares.reshape(3, 9))
print("Winner: ", board.check_for_winner())
board.print_pieces()


print("\nNo winner example: ")
board.squares = np.array([[ 1., -1.,  1.,  0.,  0.,  0.,  0.,  0.,  0.],
                          [ 0.,  2., -2.,  0.,  0.,  0.,  0.,  0.,  0.],
                          [ 0.,  0., 0.,  0.,  0.,  0.,  0.,  0.,  0.]]).flatten()
print(board.squares.reshape(3, 9))
print("Winner: ", board.check_for_winner())
board.print_pieces()


print("\nplayer_2 (-1) win horizontal: ")
board.squares = np.array([[ -1., -1.,  -1.,  0.,  0.,  0.,  0.,  0.,  0.],
                          [ 0.,   2.,   2.,  0.,  0.,  0.,  0.,  0.,  0.],
                          [ 0.,  -3,   -3.,  0.,  0.,  0.,  0.,  0.,  0.]]).flatten()
print(board.squares.reshape(3, 9))
print("Winner: ", board.check_for_winner())
board.print_pieces()


print("\nplayer_2 (-1) win vertical: ")
board.squares = np.array([[ -1., -1.,  -1.,  0.,  0.,  0.,  0.,  0.,  0.],
                          [ 0.,   0.,   2.,  0.,  0.,  0.,  0.,  0.,  0.],
                          [ 0.,  0.,   0.,  -3.,  0.,  0.,  -2.,  0.,  0.]]).flatten()
print(board.squares.reshape(3, 9))
print("Winner: ", board.check_for_winner())
board.print_pieces()


print("\nplayer_2 (-1) win diagonal: ")
board.squares = np.array([[ -1., -1.,  -1.,  0.,  0.,  0.,  0.,  0.,  0.],
                          [ 0.,   0.,   2.,  0.,  0.,  0.,  0.,  0.,  0.],
                          [ 0.,  0.,   0.,  0.,  -3.,  0.,  0.,  0.,  -2.]]).flatten()
print(board.squares.reshape(3, 9))
print("Winner: ", board.check_for_winner())
board.print_pieces()