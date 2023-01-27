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

    def get_action(self, pos, piece):
        if pos in range(9) and piece in range(1,7):
            return 9 * (piece - 1) + pos
        else:
            return -1


    # To determine the position from an action, we take the number modulo 9, resulting in a number 0-8
    def get_pos_from_action(self, action):
        return action % 9

    # To determine the piece from an action i, we use floor division by 9 (i // 9), resulting in a number 0-5, where 1-2 represent small pieces, 3-4 represent medium pieces, and 5-6 represent large pieces.
    def get_piece_from_action(self, action):
        return (action // 9) + 1

    # To determine the size of a given piece p (1-6), we use floor division by 2 (p + 1 // 2) resulting in a number 1-3
    def get_piece_size_from_action(self, action):
        piece = self.get_piece_from_action(action)
        return (piece + 1) // 2

    # Returns the index on the board [0-26] for a given action
    def get_index_from_action(self, action):
        pos = self.get_pos_from_action(action)  # [0-8]
        piece_size = self.get_piece_size_from_action(action) # [1-3]
        return pos + 9 * (piece_size - 1) # [0-26]


    # Return true if an action is legal, false otherwise
    def is_legal(self, action):
        pos = self.get_pos_from_action(action) # [0-8]
        piece = self.get_piece_from_action(action) # [1-6]
        piece_size = self.get_piece_size_from_action(action) # [1-3]
        index = self.get_index_from_action(action) # [0-26]

        board = self.squares.reshape(3, 9)

        # Check if this piece has been placed (if the piece number occurs anywhere on the level of that piece size)
        # If this piece has not been placed yet, check that it
        if any(board[piece_size-1] == piece):
            current_loc = np.where(board[piece_size-1] == piece)[0] # Returns array of values where piece is placed
            if len(current_loc) > 1: # DEBUG ONLY
                print("--ERROR-- PIECE HAS BEEN USED TWICE")
            else:
                current_loc = current_loc[0] # Current location [0-27]
            # If this piece is currently covered, moving it is not a legal action
            if self.check_covered()[current_loc] == 1:
                # print("--ERROR-- CURRENT LOCATION COVERED: ", current_loc)
                return False

        # If this piece has been placed
        # Check if the spot on the flat 3x3 board is open (we can definitely place in that case)
        flatboard = self.get_flatboard()
        if flatboard[pos] == 0:
            return True
        else:
            existing_piece_number = flatboard[pos] # [1-6]
            existing_piece_size = (abs(existing_piece_number) + 1) // 2 # [1-3]
            if piece_size > existing_piece_size:
                return True # This piece can be gobbled
            else:
                # print("--ERROR-- CURRENT PIECE CANNOT BE GOBBLED")
                # print("existing piece number: ", existing_piece_number)
                # print("existing piece size: ", existing_piece_size)
                # print("piece size: ", piece_size)
                # print("position attempted: ", pos)
                # print("index attempted: ", index)
                return False

    # Update the board with an agent's move
    def play_turn(self, agent, action):
        piece = self.get_piece_from_action(action)
        index = self.get_index_from_action(action)

        # First: check if a move is legal or not
        if not self.is_legal(action):
            print("ILLEGAL MOVE: ", action)
            return
        # If piece has already been placed, clear previous location
        if piece in self.squares:
            old_index = np.where(self.squares == piece)[0][0]
            self.squares[old_index] = 0
        if agent == 0:
            self.squares[index] = piece
        elif agent == 1:
            self.squares[index] = -1 * piece
        return

    # TODO: check if other components require the numbers to be 1 and 2 rather than -6 through 6
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

    # returns flattened board consisting of only top pieces (excluding pieces which are gobbled by other pieces)
    def get_flatboard(self):
        flatboard = np.zeros(9)
        board = self.squares.reshape(3, 9)
        for i in range(9):  # For every square in the 3x3 grid, find the topmost element (largest piece)
            top_piece_size = (np.amax(
                abs(board[:, i])))  # [-3, 2, 0] denotes a large piece gobbling a medium piece, this will return 3
            top_piece_index = list(abs(board[:, i])).index(
                top_piece_size)  # Get the row of the top piece (have to index [0]
            top_piece_color = np.sign(board[
                                          top_piece_index, i])  # Get the color of the top piece: 1 for player_1 and -1 for player_2, 0 for neither
            flatboard[i] = top_piece_color * top_piece_size # Simplify the board into only the top elements
        return flatboard

    # returns:
    # -1 for no winner
    # 0 -- agent 0 wins
    # 1 -- agent 1 wins
    def check_for_winner(self):
        winner = 0
        flatboard = self.get_flatboard()
        for combination in self.winning_combinations:
            states = []
            for index in combination:
                states.append(flatboard[index]) # default: self.squares[index]
            if all(x > 0 for x in states):
                winner = 1
            if all(x < 0 for x in states): # Change to -1 probably?
                winner = -1
        return winner

    def check_game_over(self):
        winner = self.check_for_winner()
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
