class BadTicTacToeMoveException(Exception):
    """Exception raised when a bad move is made on TicTacToe board."""

    def __init__(self, message="Bad TicTacToe move"):
        super().__init__(message)


class Board:
    def __init__(self):
        # internally self.board.squares holds a flat representation of tic tac toe board
        # where an empty board is [0, 0, 0, 0, 0, 0, 0, 0, 0]
        # where indexes are column wise order
        # 0 3 6
        # 1 4 7
        # 2 5 8

        # empty -- 0
        # player 0 -- 1
        # player 1 -- 2
        self.squares = [0] * 9

        # precommute possible winning combinations
        self.calculate_winners()

    def setup(self):
        self.calculate_winners()

    def play_turn(self, agent, pos):
        """Place a mark by the agent in the spot given.

        The following are required for a move to be valid:
        * The agent must be a known agent (either 0 or 1).
        * The spot must be be empty.
        * The spot must be in the board (integer: 0 <= spot <= 8)

        If any of those are not true, a BadTicTacToeMoveException
        will be raised.
        """
        if pos < 0 or pos > 8:
            raise BadTicTacToeMoveException("Invalid move location")
        if agent != 0 and agent != 1:
            raise BadTicTacToeMoveException("Invalid agent")
        if self.squares[pos] != 0:
            raise BadTicTacToeMoveException("Location is not empty")
        if agent == 0:
            self.squares[pos] = 1
        elif agent == 1:
            self.squares[pos] = 2
        return

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
    # 1 -- agent 0 wins
    # 2 -- agent 1 wins
    def check_for_winner(self):
        winner = -1
        for combination in self.winning_combinations:
            states = []
            for index in combination:
                states.append(self.squares[index])
            if all(x == 1 for x in states):
                winner = 1
            if all(x == 2 for x in states):
                winner = 2
        return winner

    def check_game_over(self):
        winner = self.check_for_winner()

        if winner == -1 and all(square in [1, 2] for square in self.squares):
            # tie
            return True
        elif winner in [1, 2]:
            return True
        else:
            return False

    def __str__(self):
        return str(self.squares)
