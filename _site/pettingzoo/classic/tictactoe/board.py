class Board(object):
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
        # if spot is empty
        if self.squares[pos] != 0:
            return
        if agent == 0:
            self.squares[pos] = 1
        elif agent == 1:
            self.squares[pos] = 2
        return

    def calculate_winners(self):
        winning_combinations = []
        indices = [x for x in range(0, 9)]

        # Vertical combinations
        winning_combinations += ([tuple(indices[i:(i + 3)]) for i in range(0, len(indices), 3)])

        # Horizontal combinations
        winning_combinations += [tuple([indices[x] for x in range(y, len(indices), 3)]) for y in range(0, 3)]

        # Diagonal combinations
        winning_combinations.append(tuple(x for x in range(0, len(indices), 4)))
        winning_combinations.append(tuple(x for x in range(2, len(indices) - 1, 2)))

        self.winning_combinations = winning_combinations

    # returns:
    # -1 for no winner
    # 0 -- agent 0 wins
    # 1 -- agent 1 wins
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
