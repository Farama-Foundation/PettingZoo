import itertools

# decouple pygame stuff from board logic
class Board(object):
    def __init__(self):
        # empty -- -1
        # player 0 -- 0
        # player 1 -- 1
        self.squares = [-1] * 9
        self.player = 0

        # precommute possible winning combinations
        self.calculate_winners()
        
    def setup(self):
        self.calculate_winners()
    
    def play_turn(self, agent, pos):
        # if spot is empty
        if self.squares[pos] != -1:
            return
        if self.agent == 0:
            self.squares[pos] = 0
        elif self.agent == 1:
            self.squares[pos] = 0
        return
    
    def calculate_winners(self):
        winning_combinations = []
        indices = [x for x in range(0, 9)]
        
        # Vertical combinations
        winning_combinations += ([tuple(indices[i:(i+3)]) for i in range(0, len(indices), 3)])
        
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
            if all(x == 0 for x in states):
                winner = 0
            if all(x == 1 for x in states):
                winner = 1
        return winner
    
    def check_game_over(self):
        game_over = False
        winner = self.check_for_winner()

        if winner in [0,1]: # check if someone won
            game_over = True
        elif all(square in [0, 1] for square in self.squares): # check for tie
            game_over = True
        return game_over

    def __str__(self):
        return str(self.squares)
