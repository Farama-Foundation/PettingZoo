import numpy as np

class Board:
    def __init__(self):
        # internally self.board.squares holds a representation of the gobblet board, consisting of three stacked 3x3 boards, one for each piece size.
        # We flatten it for simplicity, from [3,3,3] to [27,]

        # An empty board with the first small piece in the top left corner and the second large piece in the bottom right corner would be:
        # [[1, 0, 0, 0, 0, 0, 0, 0, 0],
        #  [0, 0, 0, 0, 0, 0, 0, 0, 0],
        #  [0, 0, 0, 0, 0, 0, 0, 0, 6]]
        # In each of the three levels (small, medum, and large pieces), an empty 3x3 board is [0, 0, 0, 0, 0, 0, 0, 0, 0]
        # where indexes are column wise order
        # 0 3 6
        # 1 4 7
        # 2 5 8

        # Reshaped to three dimensions, this would look like:
        # [[[1, 0, 0],
        #   [0, 0, 0],
        #   [0, 0, 0]],
        #  [[0, 0, 0],
        #   [0, 0, 0],
        #   [0, 0, 0]],
        #  [[0, 0, 0],
        #   [0, 0, 0],
        #   [0, 0, 6]



        # empty -- 0
        # player 0 -- 1
        # player 1 -- -1 # Default: 2
        self.squares = np.zeros(27)

        # precommute possible winning combinations
        self.calculate_winners()

    def setup(self):
        self.calculate_winners()

    def play_turn(self, agent, pos):
        # if spot is empty
        if self.squares[pos] != 0:
            return
        if agent == 0:
            self.squares[pos] = 1
        elif agent == 1:
            self.squares[pos] = 2
        return

    # TODO: check if this requires the numbers to be 1 and 2 rather than 1 and -1
    # Expects flat [9,] length array, from tic-tac-toe code
    def calculate_winners(self):
        winning_combinations = []
        indices = [x for x in range(0, 9)]

        # Vertical combinations
        winning_combinations += [
            tuple(indices[i : (i + 3)]) for i in range(0, len(indices), 3)
        ]

        # Horizontal combinations
        winning_combinations += [
            tuple(indices[x] for x in range(y, len(indices), 3)) for y in range(0, 3)
        ]

        # Diagonal combinations
        winning_combinations.append(tuple(x for x in range(0, len(indices), 4)))
        winning_combinations.append(tuple(x for x in range(2, len(indices) - 1, 2)))

        self.winning_combinations = winning_combinations

    # returns:
    # -1 for no winner
    # 0 -- agent 0 wins
    # 1 -- agent 1 wins
    def check_for_winner(self):
        winner = 0
        flatboard = np.zeros(9)
        board = self.squares.reshape(3, 9)
        for i in range(9): # For every square in the 3x3 grid, find the topmost element (largest piece)
            top_piece_size = (np.amax(abs(board[:, i]))) # [-3, 2, 0] denotes a large piece gobbling a medium piece, this will return 3
            top_piece_index = list(abs(board[:, i])).index(top_piece_size) # Get the row of the top piece (have to index [0]
            top_piece_color = np.sign(board[top_piece_index, i]) # Get the color of the top piece: 1 for player_1 and -1 for player_2, 0 for neither
            flatboard[i] = top_piece_color # Simplify the board into only the top elements
        # DEBUG
        print(flatboard)
        for combination in self.winning_combinations:
            states = []
            for index in combination:
                states.append(flatboard[index]) # default: self.squares[index]
            if all(x == 1 for x in states):
                winner = 1
            if all(x == -1 for x in states): # Change to -1 probably?
                winner = -1
        return winner

    def check_game_over(self):
        winner = self.board.check_for_winner()
        if winner in [1, -1]:
            return True
        else:
            return False

    def check_covered(self): # Return a 27 length array indicating which positions have a piece which is covered
        board = self.squares.reshape(3, 9)
        covered = np.zeros((3, 9))
        for i in range(9): # Check small pieces
            if board[0, i] != 0 and (board[1, i] != 0 or board[2, i] != 0): # If there is a small piece, and either a large or medium piece covering it
                covered[0, i] = 1
        for i in range(9): # Check medium pieces
            if board[1, i] != 0 and board[2, i] != 0: # If there is a meidum piece and a large piece covering it
                covered[1, i] = 1
        covered[2, :] = 0 # Large pieces can't be covered
        # Doesn't matter about what color is covering it, you can't move that piece this turn (allows self-gobbling)
        return covered.flatten()

# DEBUG
    def print_pieces(self):
        open_squares = [i for i in range(len(self.squares)) if self.squares[i] == 0]
        occupied_squares = [i for i in range(len(self.squares)) if self.squares[i] != 0]
        movable_squares = [i for i in occupied_squares if self.check_covered()[i] == 0]
        print("open_squares: ", open_squares)
        print("squares with pieces: ", occupied_squares)
        print("squares with uncovered pieces: ", movable_squares)

    def __str__(self):
        return str(self.squares)
