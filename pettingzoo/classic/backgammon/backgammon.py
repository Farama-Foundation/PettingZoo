import itertools
from collections import namedtuple

# Code based on: https://github.com/dellalibera/gym-backgammon

WHITE = 0
BLACK = 1
NUM_POINTS = 24
BAR = "bar"
OFF = 'off'
TOKEN = {WHITE: "X", BLACK: "O"}
COLORS = {WHITE: "White", BLACK: 'Black'}

BackgammonState = namedtuple('BackgammonState', ['board', 'bar', 'off', 'players_positions'])


# c = checker
# t = target
# s = source
# p = position


def clamp(target):
    return -1 if target < 0 else 24 if target > 23 else target


def comp1(player, x, y):
    return x < abs(y) if player == WHITE else x > (23 - abs(y))


def comp2(player, x, y):
    return x > y if player == WHITE else x < y


def comp3(player, x, y):
    return x >= y if player == WHITE else x <= y


def highest(player, positions):
    return max(positions, default=None) if player == WHITE else min(positions, default=None)


def init_board():
    board = [(0, None)] * NUM_POINTS
    board[0] = (2, BLACK)
    board[11] = (5, BLACK)
    board[16] = (3, BLACK)
    board[18] = (5, BLACK)
    board[5] = (5, WHITE)
    board[7] = (3, WHITE)
    board[12] = (5, WHITE)
    board[23] = (2, WHITE)
    return board


class Backgammon:
    def __init__(self):
        self.board = init_board()
        self.bar = [0, 0]
        self.off = [0, 0]
        self.players_home_positions = {WHITE: [5, 4, 3, 2, 1, 0], BLACK: [18, 19, 20, 21, 22, 23]}
        self.players_positions = self.get_players_positions()
        self.state = self.save_state()

    def can_bear_off(self, player):
        tot = [self.board[position][0] for position in self.players_home_positions[player] if player == self.board[position][1]]
        return sum(tot) == 15 - self.off[player]

    def could_bear_off(self, player, roll):
        # I could bear off if I use one roll to move the only checkers outside my home board, to my home board. Then I can bear off with the other roll
        tot = sum(self.board[position][0] for position in self.players_home_positions[player] if player == self.board[position][1])
        threshold = 15 - 1 if len(roll) == 2 else 15 - 3
        return tot >= (threshold - self.off[player])

    def can_move_to(self, player, target):
        if target < 0 or target > 23:
            return self.can_bear_off(player)
        return self.board[target][0] < 2 or (self.board[target][0] > 1 and self.board[target][1] == player)

    def is_valid(self, player, target):
        if 0 <= target < NUM_POINTS:
            return self.board[target][0] < 2 or (self.board[target][0] > 1 and self.board[target][1] == player)
        return False

    # =================================================================================
    # NORMAL PLAYS ====================================================================
    # =================================================================================
    def get_normal_plays(self, player, roll):
        # Generate normal legal plays (not bear off moves)
        plays = set()

        positions = self.players_positions[player]
        combinations_positions = list(itertools.combinations(positions, 2))

        for s in positions:
            if self.board[s][0] > 1:
                combinations_positions.append((s, s))

            if self.is_valid(player, s + roll[0]) and self.is_valid(player, s + roll[0] + roll[1]):
                plays.add(((s, s + roll[0]), (s + roll[0], s + roll[0] + roll[1])))

            if self.is_valid(player, s + roll[1]) and self.is_valid(player, s + roll[0] + roll[1]):
                plays.add(((s, s + roll[1]), (s + roll[1], s + roll[0] + roll[1])))

        for (s1, s2) in combinations_positions:
            t1 = s1 + roll[0]
            t2 = s1 + roll[1]
            t3 = s2 + roll[0]
            t4 = s2 + roll[1]
            t_far1 = s1 + roll[0] + roll[1]
            t_far2 = s2 + roll[0] + roll[1]

            if self.is_valid(player, t1) and self.is_valid(player, t4):
                plays.add(((s1, t1), (s2, t4)))

            if s1 != s2 and self.is_valid(player, t2) and self.is_valid(player, t3):  # if (s1 == s2) => (target1 == target3 and target2 == target4). Same move as before, but swapped
                plays.add(((s1, t2), (s2, t3)))

            if self.is_valid(player, t1) and self.is_valid(player, t_far1):
                plays.add(((s1, t1), (t1, t_far1)))

            if self.is_valid(player, t2) and self.is_valid(player, t_far1):
                plays.add(((s1, t2), (t2, t_far1)))

            if s1 != s2 and self.is_valid(player, t3) and self.is_valid(player, t_far2):  # if (s1 == s2) => (target_far1 == target_far2)
                plays.add(((s2, t3), (t3, t_far2)))

            if s1 != s2 and self.is_valid(player, t4) and self.is_valid(player, t_far2):  # if (s1 == s2) => (target_far1 == target_far2)
                plays.add(((s2, t4), (t4, t_far2)))

        if len(plays) == 0:
            # https://bkgm.com/faq/BasicRules.html#what_if_i_can_only_play_one_number_
            # "If you can play one number but not both, then you must play the higher one."
            r = min(roll) if player == WHITE else max(roll)
            single_moves = self.get_single_moves(player, r)

            if len(single_moves) == 0:
                # get the other roll
                r = max(roll) if player == WHITE else min(roll)
                single_moves = self.get_single_moves(player, r)

            for move in single_moves:
                plays.add((move,))

        return plays

    # NORMAL PLAYS - DOUBLE ===========================================================
    def get_normal_plays_double(self, player, roll):
        plays = set()
        r = roll[0]

        sources = {
            1: [p for p in self.players_positions[player] if self.board[p][0] > 0],
            2: [p for p in self.players_positions[player] if self.board[p][0] > 1],
            3: [p for p in self.players_positions[player] if self.board[p][0] > 2],
            4: [p for p in self.players_positions[player] if self.board[p][0] > 3],
        }

        combo2 = set(itertools.combinations(sources[1], 2))
        combo3 = set(itertools.combinations(sources[1], 3))

        for s1 in sources[4]:
            if self.is_valid(player, s1 + r):
                plays.add(((s1, s1 + r), (s1, s1 + r), (s1, s1 + r), (s1, s1 + r)))

        for s1 in sources[3]:
            if self.is_valid(player, s1 + r):
                plays.add(((s1, s1 + r), (s1, s1 + r), (s1, s1 + r)))

                for s2 in sources[1]:
                    if s1 != s2 and self.is_valid(player, s2 + r):
                        plays.add(((s1, s1 + r), (s1, s1 + r), (s1, s1 + r), (s2, s2 + r)))

                target_far = s1 + r + r
                if self.is_valid(player, target_far):
                    plays.add(((s1, s1 + r), (s1, s1 + r), (s1, s1 + r), (s1 + r, target_far)))

        for s1 in sources[2]:
            if self.is_valid(player, s1 + r):
                plays.add(((s1, s1 + r), (s1, s1 + r)))

                for (s2, s3) in combo2:
                    if s1 != s2 and s1 != s3 and self.is_valid(player, s2 + r) and self.is_valid(player, s3 + r):
                        plays.add(((s1, s1 + r), (s1, s1 + r), (s2, s2 + r), (s3, s3 + r)))

                for s2 in sources[2]:
                    if s1 != s2 and self.is_valid(player, s2 + r):
                        plays.add(((s1, s1 + r), (s1, s1 + r), (s2, s2 + r), (s2, s2 + r)))

                for s2 in sources[1]:
                    if s1 != s2 and self.is_valid(player, s2 + r):
                        plays.add(((s1, s1 + r), (s1, s1 + r), (s2, s2 + r)))

                        target_far = s1 + r + r
                        if self.is_valid(player, target_far):
                            plays.add(((s1, s1 + r), (s1, s1 + r), (s1 + r, target_far), (s2, s2 + r)))

                        target_far = s2 + r + r
                        if self.is_valid(player, target_far):
                            plays.add(((s1, s1 + r), (s1, s1 + r), (s2, s2 + r), (s2 + r, target_far)))

                target_far = s1 + r + r
                if self.is_valid(player, target_far):
                    plays.add(((s1, s1 + r), (s1, s1 + r), (s1 + r, target_far), (s1 + r, target_far)))

                    target_far2 = s1 + r + r + r
                    if self.is_valid(player, target_far2):
                        plays.add(((s1, s1 + r), (s1, s1 + r), (s1 + r, target_far), (target_far, target_far2)))

        for s1 in sources[1]:
            if self.is_valid(player, s1 + r):
                plays.add(((s1, s1 + r),))

                target_far1 = s1 + r + r
                target_far2 = s1 + r + r + r
                target_far3 = s1 + r + r + r + r

                if self.is_valid(player, target_far1):
                    plays.add(((s1, s1 + r), (s1 + r, target_far1)))

                    if self.is_valid(player, target_far2):
                        plays.add(((s1, s1 + r), (s1 + r, target_far1), (target_far1, target_far2)))

                        if self.is_valid(player, target_far3):
                            plays.add(((s1, s1 + r), (s1 + r, target_far1), (target_far1, target_far2), (target_far2, target_far3)))

                        for s2 in sources[1]:
                            if s2 != s1 and self.is_valid(player, s2 + r):
                                plays.add(((s1, s1 + r), (s1 + r, target_far1), (target_far1, target_far2), (s2, s2 + r)))

                    for s2 in sources[1]:
                        if s1 != s2 and self.is_valid(player, s2 + r):
                            plays.add(((s1, s1 + r), (s1 + r, target_far1), (s2, s2 + r)))

                            s2_target_far1 = s2 + r + r

                            if self.is_valid(player, s2_target_far1):
                                plays.add(((s1, s1 + r), (s1 + r, target_far1), (s2, s2 + r), (s2 + r, s2_target_far1)))

                for s2 in sources[1]:
                    if s1 != s2 and self.is_valid(player, s2 + r):
                        plays.add(((s1, s1 + r), (s2, s2 + r)))

                for (s2, s3, s4) in combo3:
                    if s1 != s2 and s1 != s3 and s1 != s4 \
                            and self.is_valid(player, s2 + r) and self.is_valid(player, s3 + r) and self.is_valid(player, s4 + r):
                        plays.add(((s1, s1 + r), (s2, s2 + r), (s3, s3 + r), (s4, s4 + r)))

                for (s2, s3) in combo2:
                    if s1 != s2 and s1 != s3 and self.is_valid(player, s2 + r) and self.is_valid(player, s3 + r):
                        plays.add(((s1, s1 + r), (s2, s2 + r), (s3, s3 + r)))

                        if self.is_valid(player, target_far1):
                            plays.add(((s1, s1 + r), (s1 + r, target_far1), (s2, s2 + r), (s3, s3 + r)))
        return plays

    # =================================================================================
    # BEAR OFF PLAYS ==================================================================
    # =================================================================================
    def move_to_go_home(self, player, r, out_of_home):
        # I try to move all the checkers to home board, so I can start to bear off. I can use at most 3 rolls, so I can use the last one for a bear off move
        move = ()

        home_positions = set(self.players_home_positions[player])

        if len(out_of_home) == 1:  # there is 1 position where there is/are checker(s) out of home
            out = out_of_home[0]

            if self.board[out][0] <= 3:
                t1 = out + r
                t2 = t1 + r
                t3 = t2 + r

                move1 = (out, clamp(t1))
                move2 = (t1, clamp(t2))
                move3 = (t2, clamp(t3))

                if self.is_valid(player, t1):
                    if t1 in home_positions:  # I used 1 die to move 1 checker from the only position out of home board, to home board
                        if self.board[out][0] == 1:
                            move = (move1,)
                        elif self.board[out][0] == 2:
                            move = (move1, move1)
                        elif self.board[out][0] == 3:
                            move = (move1, move1, move1)
                    else:
                        if self.is_valid(player, t2) and self.board[out][0] == 1:
                            if t2 in home_positions:  # I used 2 dice to move 1 checker from the only position out of home board, to home board
                                move = (move1, move2)
                            else:
                                if self.is_valid(player, t3):
                                    if t3 in home_positions:  # I used 3 dice to move 1 checker from the only position out of home board to home board
                                        move = (move1, move2, move3)

        elif len(out_of_home) == 2:  # there are 2 positions where there is/are checker(s) out of home
            out1 = out_of_home[0]
            out2 = out_of_home[1]

            if (self.board[out1][0] + self.board[out2][0]) <= 3:

                t11 = out1 + r
                t21 = t11 + r

                t12 = out2 + r
                t22 = t12 + r

                move11 = (out1, clamp(t11))
                move21 = (t11, clamp(t21))

                move12 = (out2, clamp(t12))
                move22 = (t12, clamp(t22))

                if self.is_valid(player, t11) and self.is_valid(player, t12):

                    if t11 in home_positions and t12 in home_positions:
                        move = (move11, move12)

                        if self.board[out1][0] == 1 and self.board[out2][0] == 2:
                            move = (move11, move12, move12)
                        elif self.board[out2][0] == 1 and self.board[out1][0] == 2:
                            move = (move11, move11, move12)

                    elif t11 in home_positions and self.board[out1][0] == 1 and self.board[out2][0] == 1:
                        if self.is_valid(player, t22):
                            if t22 in home_positions:
                                move = (move11, move12, move22)

                    elif t12 in home_positions and self.board[out1][0] == 1 and self.board[out2][0] == 1:
                        if self.is_valid(player, t21):
                            if t21 in home_positions:
                                move = (move12, move11, move21)

        elif len(out_of_home) == 3:
            out1 = out_of_home[0]
            out2 = out_of_home[1]
            out3 = out_of_home[2]

            if self.is_valid(player, out1 + r) and self.is_valid(player, out2 + r) and self.is_valid(player, out3 + r) \
                    and self.board[out1][0] == 1 and self.board[out2][0] == 1 and self.board[out3][0] == 1 \
                    and (out1 + r) in home_positions and (out2 + r) in home_positions and (out3 + r) in home_positions:
                move = ((out1, out1 + r), (out2, out2 + r), (out3, out3 + r))

        return move

    def get_bear_off_plays(self, player, roll):
        """
        http://usbgf.org/learn-backgammon/backgammon-rules-and-terms/rules-of-backgammon/
        A player bears off a checker by rolling a number that corresponds to the point on which the checker resides, and then removing that checker from the board.
        Thus, rolling a 6 permits the player to remove a checker from the six point. If there is no checker on the point indicated by the roll, the player must make a legal move using a checker on a higher-numbered point.
        If there are no checkers on higher-numbered points, the player is permitted (and required) to remove a checker from the highest point on which one of his checkers resides.
        A player is under no obligation to bear off if he can make an otherwise legal move.

        https://en.wikipedia.org/wiki/Backgammon#Bearing_off
        When all of a player's checkers are in that player's home board, that player may start removing them; this is called "bearing off".
        A roll of 1 may be used to bear off a checker from the 1-point, a 2 from the 2-point, and so on.
        If all of a player's checkers are on points lower than the number showing on a particular die, the player may use that die to bear off one checker from the highest occupied point
        """
        plays = set()
        reverse = player != WHITE
        r1, r2 = sorted(roll, reverse=reverse)  # for WHITE player the rolls are negative (i.e (-3,-2))

        active_positions = set(self.players_positions[player])
        home_positions = set(self.players_home_positions[player])

        # Point on which the checker resides from which I can bear off
        s1 = abs(r1) - 1 if player == WHITE else NUM_POINTS - abs(r1)
        s2 = abs(r2) - 1 if player == WHITE else NUM_POINTS - abs(r2)

        if self.can_bear_off(player):

            if s1 in active_positions:
                move = (s1, s1 + r1)
                plays.add((move,))
                src = [s for s in active_positions if s1 != s or not (s1 == s and self.board[s1][0] == 1)]
                plays.update([(move, single) for single in self.get_single_moves(player, roll=r2, player_src=src)])

            if s2 in active_positions:
                move = (s2, clamp(s2 + r2))
                plays.add((move,))
                src = [s for s in active_positions if s2 != s or not (s2 == s and self.board[s2][0] == 1)]
                plays.update([(move, single) for single in self.get_single_moves(player, roll=r1, player_src=src)])

            if s1 in active_positions and s2 in active_positions:
                plays.add(((s1, clamp(s1 + r1)), (s2, clamp(s2 + r2))))

            for s in active_positions:
                # Check if I can be in a valid bear off position (s1 or s2)
                t1 = s + r1
                t2 = s + r2
                if self.is_valid(player, t1) and t1 == s2:
                    plays.add(((s, t1), (s2, clamp(s2 + r2))))
                if self.is_valid(player, t2) and t2 == s1:
                    plays.add(((s, t2), (s1, clamp(s1 + r1))))

            # checkers that are higher than the maximum roll (i.e. if the roll is (2,3), the highest checkers are the checkers in position 4,5,6,... (if player WHITE is the current player))
            highest_src = {s for s in active_positions if comp2(player, s, s1)}

            # If there are no checkers on higher-numbered points,...
            if len(highest_src) == 0:
                # ... the player is permitted (and required) to remove a checker from the highest point on which one of his checkers resides.
                s1_best = highest(player, [s for s in active_positions if comp1(player, s, r1)])

                if s1_best is not None:
                    move = (s1_best, clamp(s1_best + r1))
                    plays.add((move,))

                    for s in active_positions:
                        if self.is_valid(player, s + r2) and not (s == s1_best and self.board[s1_best][0] == 1):
                            plays.add((move, (s, s + r2)))

                    if self.board[s1_best][0] == 1:
                        active_positions -= {s1_best}

                    s2_best = highest(player, [s for s in active_positions if comp1(player, s, r1)])

                    if s2_best is not None and self.can_move_to(player, s2_best + r2):
                        plays.add((move, (s2_best, clamp(s2_best + r2))))

                    if s2 in active_positions:
                        plays.add((move, (s2, clamp(s2 + r2))))

                    # move from the highest position with the lower roll, and then check if I can bear off with the other roll
                    if self.is_valid(player, s1_best + r2) and self.board[s1_best][0] == 1:
                        move = (s1_best, (s1_best + r2))

                        active_positions.add(s1_best + r2)

                        s2_best = highest(player, [s for s in active_positions if comp1(player, s, r1)])

                        if s2_best is not None and self.can_move_to(player, s2_best + r1):
                            plays.add((move, (s2_best, clamp(s2_best + r1))))

            elif len(highest_src) == 1:
                # Here I have only one position that is higher than than the maximum roll
                s = list(highest_src)[0]

                if self.is_valid(player, s + r2) and self.board[s][0] == 1:

                    if comp3(player, s1, s + r2):
                        tmp = set(list(active_positions)[:])
                        tmp -= {s}
                        tmp.add(s + r2)

                        s1_best = highest(player, [s for s in tmp if comp1(player, s, r1)])
                        move = (s, clamp(s + r2))

                        if s1_best is not None:

                            higher_src1 = {s for s in tmp if comp2(player, s, s1_best)}

                            if len(higher_src1) == 0:
                                plays.add((move, (s1_best, clamp(s1_best + r1))))

                if self.is_valid(player, s + r1) and self.board[s][0] == 1:

                    if comp3(player, s2, s + r1):
                        tmp = set(list(active_positions)[:])
                        tmp -= {s}
                        tmp.add(s + r1)

                        s1_best = highest(player, [s for s in tmp if comp1(player, s, r2)])
                        move = (s, clamp(s + r1))

                        if s1_best is not None:

                            higher_src1 = {s for s in tmp if comp2(player, s, s1_best)}

                            if len(higher_src1) == 0:
                                plays.add((move, (s1_best, clamp(s1_best + r2))))

        else:
            candidate_src = [s for s in active_positions if s not in home_positions]
            assert len(candidate_src) == 1, print(f"Should be 1 instead of {candidate_src}")
            candidate_src = candidate_src[0]
            t1 = candidate_src + r1
            t2 = candidate_src + r2

            if self.is_valid(player, t1) and t1 in home_positions:
                tmp = set(list(active_positions)[:])
                tmp -= {candidate_src}
                tmp.add(t1)
                highest_src = {s for s in tmp if comp2(player, s, s2)}

                if s2 in tmp:
                    plays.add(((candidate_src, t1), (s2, clamp(s2 + r2))))

                elif comp3(player, s2, t1) and len(highest_src) == 0:
                    s_best = highest(player, [s for s in tmp if comp1(player, s, r2)])

                    if s_best is not None:
                        plays.add(((candidate_src, t1), (s_best, clamp(s_best + r2))))

            if self.is_valid(player, t2) and t2 in home_positions:
                tmp = set(list(active_positions)[:])
                tmp -= {candidate_src}
                tmp.add(t2)
                highest_src = {s for s in tmp if comp2(player, s, s1)}

                if s1 in tmp:
                    plays.add(((candidate_src, t2), (s1, clamp(s1 + r1))))

                elif comp3(player, s1, t2):
                    s_best = highest(player, [s for s in tmp if comp1(player, s, r1)])

                    if s_best is not None and ((len(highest_src) == 1 and list(highest_src)[0] == s_best) or len(highest_src) == 0):
                        plays.add(((candidate_src, t2), (s_best, clamp(s_best + r1))))

        return plays

    # BEAR OFF PLAYS - DOUBLE =========================================================
    def get_bear_off_play_double(self, player, roll):
        plays = set()
        r = roll[0]
        old_state = self.save_state()

        home_positions = set(self.players_home_positions[player])
        # position from which I could bear off
        s1 = abs(r) - 1 if player == WHITE else NUM_POINTS - abs(r)
        move = (s1, clamp(s1 + r))

        out_of_home = [s for s in set(self.players_positions[player]) if s not in home_positions]
        # Actions needed to move the checkers (if any) that are out of home, to home board
        out_of_home_move = self.move_to_go_home(player, r, out_of_home)
        if len(out_of_home_move) > 0:
            # I execute the move needed to move all the checkers that are not in home board to home board (in order to update the board - I saved the state)
            self.execute_play(player, out_of_home_move)
            self.players_positions = self.get_players_positions()
        assert len(list(out_of_home_move)) <= 3, print(f"Should be <= 3 instead of {out_of_home_move}")
        # number of dice used to move all the checkers that are not in home board to home board (should be <= 3)
        dice_used = len(out_of_home_move)

        if self.can_bear_off(player):
            # All the checkers are in the home board
            active_positions = set(self.players_positions[player])
            # checkers that are higher than position from which I could bear off
            higher_src = {s for s in active_positions if comp2(player, s, s1)}

            single_moves = self.get_single_moves(player, roll=r)
            double_moves = self.get_double_moves(player, roll=r, single_moves=single_moves)
            triple_moves = self.get_triple_moves(player, roll=r, double_moves=double_moves)

            # I have a checker on the exact position from which I can bear off
            if s1 in active_positions:
                if dice_used == 0:
                    if self.board[s1][0] >= 1:
                        plays.add((move,))
                        plays.update([(move, single) for single in single_moves])
                        plays.update([(move, double[0], double[1]) for double in double_moves])
                        plays.update([(move, triple[0], triple[1], triple[2]) for triple in triple_moves])

                    if self.board[s1][0] >= 2:
                        plays.add((move, move))
                        plays.update([(move, move, single) for single in single_moves])
                        plays.update([(move, move, double[0], double[1]) for double in double_moves])

                    if self.board[s1][0] >= 3:
                        plays.add((move, move, move))
                        plays.update([(move, move, move, single) for single in single_moves])

                    if self.board[s1][0] >= 4:
                        plays.add((move, move, move, move))
                elif dice_used == 1:
                    if self.board[s1][0] >= 1:
                        plays.add(out_of_home_move + (move, ))
                        plays.update([(out_of_home_move + (move, ) + (single, )) for single in single_moves])
                        plays.update([(out_of_home_move + (move, ) + (double[0], ) + (double[1], )) for double in double_moves])

                    if self.board[s1][0] >= 2:
                        plays.add(out_of_home_move + (move, ) + (move, ))
                        plays.update([(out_of_home_move + (move, ) + (move, ) + (single, )) for single in single_moves])

                    if self.board[s1][0] >= 3:
                        plays.add(out_of_home_move + (move, ) + (move, ) + (move, ))
                elif dice_used == 2:
                    if self.board[s1][0] >= 1:
                        plays.add(out_of_home_move + (move, ))
                        plays.update([(out_of_home_move + (move, ) + (single, )) for single in single_moves])

                    if self.board[s1][0] >= 2:
                        plays.add(out_of_home_move + (move, ) + (move, ))
                elif dice_used == 3:
                    if self.board[s1][0] >= 1:
                        plays.add(out_of_home_move + (move, ))

                for s in active_positions:
                    if dice_used == 0:
                        t1 = s + r
                        if self.is_valid(player, t1):
                            if t1 == s1:
                                plays.add((move, (s, t1)))
                                if self.board[s1][0] >= 1:
                                    plays.add((move, move, (s, t1)))
                                    plays.update([(move, move, (s, t1), single) for single in single_moves if single != (s, t1)])

                                if self.board[s1][0] >= 2:
                                    plays.add((move, move, move, (s, t1)))
                            else:
                                t2 = t1 + r
                                if self.is_valid(player, t2):
                                    if t2 == s1:
                                        plays.add((move, (s, t1), (t1, t2)))
                                        if self.board[s1][0] >= 1:
                                            plays.add((move, move, (s, t1), (t1, t2)))
                    elif dice_used == 1:
                        t1 = s + r
                        if self.is_valid(player, t1):
                            if t1 == s1:
                                plays.add(out_of_home_move + (move,) + ((s, t1), ))
                                if self.board[s1][0] >= 1:
                                    plays.add(out_of_home_move + (move, ) + (move, ) + ((s, t1), ))
                            else:
                                t2 = t1 + r
                                if self.is_valid(player, t2):
                                    if t2 == s1:
                                        plays.add(out_of_home_move + (move, ) + ((s, t1), ) + ((t1, t2), ))
                    elif dice_used == 2:
                        t1 = s + r
                        if self.is_valid(player, t1):
                            if t1 == s1:
                                plays.add(out_of_home_move + (move,) + ((s, t1),))

            # I don't have a checker on the exact position from which I can bear off, but I try to move higher checkers to that position
            for s in higher_src:
                if dice_used == 0:
                    t1 = s + r
                    if self.is_valid(player, t1):
                        if t1 == s1:
                            if self.board[s][0] >= 1:
                                plays.add(((s, t1), move))
                                if self.board[s][0] == 1:
                                    tmp = active_positions - {s}  # remove the source from active position so I can generate consistent single moves
                                    tmp_single_moves = self.get_single_moves(player, roll=r, player_src=tmp)
                                    tmp_double_moves = self.get_double_moves(player, roll=r, single_moves=tmp_single_moves)
                                    plays.update([((s, t1), move, single) for single in tmp_single_moves])
                                    plays.update([((s, t1), move, double[0], double[1]) for double in tmp_double_moves])
                                else:
                                    plays.update([((s, t1), move, single) for single in single_moves])

                                    if self.board[s][0] == 2:
                                        tmp = active_positions - {s}  # remove the source from active position so I can generate consistent single moves
                                        tmp_single_moves = self.get_single_moves(player, roll=r, player_src=tmp)
                                        tmp_double_moves = self.get_double_moves(player, roll=r, single_moves=tmp_single_moves)
                                        plays.update([((s, t1), move, double[0], double[1]) for double in tmp_double_moves])
                                    else:
                                        plays.update([((s, t1), move, double[0], double[1]) for double in double_moves])

                            if self.board[s][0] >= 2:
                                plays.add(((s, t1), (s, t1), move, move))
                            if self.board[s][0] >= 3:
                                plays.add(((s, t1), (s, t1), (s, t1), move))
                        else:
                            t2 = s + r + r
                            if self.is_valid(player, t2):
                                if t2 == s1:
                                    if self.board[s][0] >= 1:
                                        plays.add(((s, t1), (t1, t2), move))

                                        if self.board[s][0] == 1:
                                            tmp = active_positions - {s}
                                            tmp_single_moves = self.get_single_moves(player, roll=r, player_src=tmp)
                                            plays.update([((s, t1), (t1, t2), move, single) for single in tmp_single_moves])
                                        else:
                                            plays.update([((s, t1), (t1, t2), move, single) for single in single_moves])

                                    if self.board[s][0] >= 2:
                                        plays.add(((s, t1), (s, t1), (t1, t2), move))
                                else:
                                    t3 = s + r + r + r
                                    if self.is_valid(player, t3):
                                        if t3 == s1:
                                            if self.board[s][0] == 1:
                                                plays.add(((s, t1), (t1, t2), (t2, t3), move))
                elif dice_used == 1:
                    t1 = s + r
                    if self.is_valid(player, t1):
                        if t1 == s1:
                            if self.board[s][0] >= 1:
                                plays.add(out_of_home_move + ((s, t1),) + (move,))

                                if self.board[s][0] == 1:
                                    tmp = active_positions - {s}
                                    tmp_single_moves = self.get_single_moves(player, roll=r, player_src=tmp)
                                    plays.update([(out_of_home_move + ((s, t1),) + (move, ) + (single, )) for single in tmp_single_moves])
                                else:
                                    plays.update([(out_of_home_move + ((s, t1),) + (move, ) + (single, )) for single in single_moves])

                            if self.board[s][0] >= 2:
                                plays.add(out_of_home_move + ((s, t1),) + ((s, t1),) + (move,))
                        else:
                            t2 = s + r + r
                            if self.is_valid(player, t2):
                                if t2 == s1:
                                    if self.board[s][0] >= 1:
                                        plays.add(out_of_home_move + ((s, t1),) + ((t1, t2),) + (move,))
                elif dice_used == 2:
                    t1 = s + r
                    if self.is_valid(player, t1):
                        if t1 == s1:
                            if self.board[s][0] >= 1:
                                plays.add(out_of_home_move + ((s, t1),) + (move,))
            if len(higher_src) == 0:
                s1_highest = highest(player, [s for s in active_positions if comp1(player, s, r)])
                active_positions -= {s1_highest}

                s2_highest = highest(player, [s for s in active_positions if comp1(player, s, r)])
                active_positions -= {s2_highest}

                s3_highest = highest(player, [x for x in active_positions if comp1(player, x, r)])
                active_positions -= {s3_highest}

                s4_highest = highest(player, [x for x in active_positions if comp1(player, x, r)])

                # I don't have higher checkers than the position from which I can bear off
                if s1_highest is not None:
                    move1 = (s1_highest, clamp(s1_highest + r))

                    if dice_used == 0:
                        if self.board[s1_highest][0] == 1:
                            plays.add((move1,))

                            if s2_highest is not None:
                                move2 = (s2_highest, clamp(s2_highest + r))

                                if self.board[s2_highest][0] == 1:
                                    plays.add((move1, move2))

                                    if s3_highest is not None:
                                        move3 = (s3_highest, clamp(s3_highest + r))

                                        if self.board[s3_highest][0] == 1:
                                            plays.add((move1, move2, move3))

                                            if s4_highest is not None:
                                                move4 = (s4_highest, clamp(s4_highest + r))
                                                plays.add((move1, move2, move3, move4))

                                        elif self.board[s3_highest][0] >= 2:
                                            plays.add((move1, move2, move3, move3))

                                elif self.board[s2_highest][0] == 2:
                                    plays.add((move1, move2, move2))

                                    if s3_highest is not None:
                                        move3 = (s3_highest, clamp(s3_highest + r))
                                        plays.add((move1, move2, move2, move3))

                                elif self.board[s2_highest][0] >= 3:
                                    plays.add((move1, move2, move2, move2))

                        elif self.board[s1_highest][0] == 2:
                            plays.add((move1, move1))

                            if s2_highest is not None:
                                move2 = (s2_highest, clamp(s2_highest + r))

                                if self.board[s2_highest][0] == 1:
                                    plays.add((move1, move1, move2))

                                    if s3_highest is not None:
                                        move3 = (s3_highest, clamp(s3_highest + r))
                                        plays.add((move1, move1, move2, move3))

                                elif self.board[s2_highest][0] >= 2:
                                    plays.add((move1, move1, move2, move2))

                        elif self.board[s1_highest][0] == 3:
                            plays.add((move1, move1, move1))

                            if s2_highest is not None:
                                move2 = (s2_highest, clamp(s2_highest + r))
                                plays.add((move1, move1, move1, move2))

                        elif self.board[s1_highest][0] >= 4:
                            plays.add((move1, move1, move1, move1))

                    elif dice_used == 1:
                        if self.board[s1_highest][0] == 1:
                            plays.add(out_of_home_move + (move1,))

                            if s2_highest is not None:
                                move2 = (s2_highest, clamp(s2_highest + r))

                                if self.board[s2_highest][0] == 1:
                                    plays.add(out_of_home_move + (move1,) + (move2, ))

                                    if s3_highest is not None:
                                        move3 = (s3_highest, clamp(s3_highest + r))

                                        if self.board[s3_highest][0] >= 1:
                                            plays.add(out_of_home_move + (move1, ) + (move2, ) + (move3, ))

                                elif self.board[s2_highest][0] >= 2:
                                    plays.add(out_of_home_move + (move1, ) + (move2, ) + (move2, ))

                        elif self.board[s1_highest][0] == 2:
                            plays.add(out_of_home_move + (move1,) + (move1, ))

                            if s2_highest is not None:
                                move2 = (s2_highest, clamp(s2_highest + r))

                                if self.board[s2_highest][0] >= 1:
                                    plays.add(out_of_home_move + (move1,) + (move1,) + (move2, ))

                        elif self.board[s1_highest][0] >= 3:
                            plays.add(out_of_home_move + (move1,) + (move1,) + (move1, ))

                    elif dice_used == 2:
                        if self.board[s1_highest][0] == 1:
                            plays.add(out_of_home_move + (move1,))

                            if s2_highest is not None:
                                move2 = (s2_highest, clamp(s2_highest + r))

                                if self.board[s2_highest][0] >= 1:
                                    plays.add(out_of_home_move + (move1,) + (move2,))

                        elif self.board[s1_highest][0] >= 2:
                            plays.add(out_of_home_move + (move1,) + (move1,))

                    elif dice_used == 3:
                        plays.add(out_of_home_move + (move1,))

            if len(higher_src) == 1:
                if dice_used == 0:

                    high_src = list(higher_src)[0]
                    active_positions -= {high_src}

                    t1 = high_src + r
                    t2 = t1 + r
                    t3 = t2 + r

                    move1 = (high_src, clamp(t1))
                    move2 = (t1, clamp(t2))
                    move3 = (t2, clamp(t3))

                    if self.is_valid(player, t1):

                        if self.board[high_src][0] == 1:

                            if comp3(player, s1, t1):
                                active_positions.add(t1)
                                s1_highest = highest(player, [s for s in active_positions if comp1(player, s, r)])

                                if s1_highest is not None:
                                    if self.board[s1_highest][1] != player:
                                        c1 = self.board[high_src][0]
                                    else:
                                        c1 = (self.board[s1_highest][0] + 1) if t1 == s1_highest else self.board[s1_highest][0]

                                    active_positions -= {s1_highest}
                                    move_s1 = (s1_highest, clamp(s1_highest + r))

                                    if c1 == 1:
                                        s2_highest = highest(player, [s for s in active_positions if comp1(player, s, r)])
                                        plays.add((move1, move_s1))

                                        if s2_highest is not None:
                                            if self.board[s2_highest][1] != player:
                                                c2 = 1
                                            else:
                                                c2 = (self.board[s2_highest][0] + 1) if t1 == s2_highest else self.board[s2_highest][0]
                                            active_positions -= {s2_highest}
                                            move_s2 = (s2_highest, clamp(s2_highest + r))

                                            if c2 == 1:
                                                s3_highest = highest(player, [s for s in active_positions if comp1(player, s, r)])
                                                plays.add((move1, move_s1, move_s2))

                                                if s3_highest is not None:
                                                    move_s3 = (s3_highest, clamp(s3_highest + r))
                                                    plays.add((move1, move_s1, move_s2, move_s3))

                                            elif c2 >= 2:
                                                plays.add((move1, move_s1, move_s2, move_s2))

                                    elif c1 == 2:
                                        plays.add((move1, move_s1, move_s1))
                                        s2_highest = highest(player, [s for s in active_positions if comp1(player, s, r)])

                                        if s2_highest is not None:
                                            move_s2 = (s2_highest, clamp(s2_highest + r))
                                            plays.add((move1, move_s1, move_s1, move_s2))

                                    elif c1 >= 3:
                                        plays.add((move1, move_s1, move_s1, move_s1))

                            elif self.is_valid(player, t2):

                                if comp3(player, s1, t2):
                                    active_positions.add(t2)
                                    s1_highest = highest(player, [s for s in active_positions if comp1(player, s, r)])

                                    if s1_highest is not None:
                                        if self.board[s1_highest][1] != player:
                                            c1 = self.board[high_src][0]
                                        else:
                                            c1 = (self.board[s1_highest][0] + 1) if t2 == s1_highest else self.board[s1_highest][0]
                                        active_positions -= {s1_highest}
                                        move_s1 = (s1_highest, clamp(s1_highest + r))

                                        if c1 == 1:
                                            s2_highest = highest(player, [s for s in active_positions if comp1(player, s, r)])
                                            plays.add((move1, move2, move_s1))

                                            if s2_highest is not None:
                                                move_s2 = (s2_highest, clamp(s2_highest + r))
                                                plays.add((move1, move2, move_s1, move_s2))

                                        elif c1 >= 2:
                                            plays.add((move1, move2, move_s1, move_s1))

                                elif self.is_valid(player, t3):

                                    if comp3(player, s1, t3):
                                        active_positions.add(t3)
                                        s1_highest = highest(player, [s for s in active_positions if comp1(player, s, r)])

                                        if s1_highest is not None:
                                            move_s1 = (s1_highest, clamp(s1_highest + r))
                                            plays.add((move1, move2, move3, move_s1))

                        elif self.board[high_src][0] == 2:

                            if comp3(player, s1, t1):
                                active_positions.add(t1)
                                s1_highest = highest(player, [s for s in active_positions if comp1(player, s, r)])

                                if s1_highest is not None:
                                    if self.board[s1_highest][1] != player:
                                        c1 = self.board[high_src][0]
                                    else:
                                        c1 = (self.board[s1_highest][0] + 1) if t1 == s1_highest else self.board[s1_highest][0]
                                    move_s1 = (s1_highest, clamp(s1_highest + r))

                                    if c1 == 1:
                                        active_positions -= {s1_highest}
                                        s2_highest = highest(player, [s for s in active_positions if comp1(player, s, r)])
                                        plays.add((move1, move1, move_s1))

                                        if s2_highest is not None:
                                            move_s2 = (s2_highest, clamp(s2_highest + r))
                                            plays.add((move1, move1, move_s1, move_s2))

                                    elif c1 >= 2:
                                        plays.add((move1, move1, move_s1, move_s1))

                        elif self.board[high_src][0] == 3:

                            if comp3(player, s1, t1):
                                active_positions.add(t1)
                                s1_highest = highest(player, [s for s in active_positions if comp1(player, s, r)])

                                if s1_highest is not None:
                                    move_s1 = (s1_highest, clamp(s1_highest + r))
                                    plays.add((move1, move1, move1, move_s1))

                if dice_used == 1:
                    high_src = list(higher_src)[0]
                    active_positions -= {high_src}

                    t1 = high_src + r
                    t2 = t1 + r

                    move1 = (high_src, clamp(t1))
                    move2 = (t1, clamp(t2))

                    if self.is_valid(player, t1):

                        if self.board[high_src][0] == 1:

                            if comp3(player, s1, t1):
                                active_positions.add(t1)
                                s1_highest = highest(player, [s for s in active_positions if comp1(player, s, r)])

                                if s1_highest is not None:
                                    if self.board[s1_highest][1] != player:
                                        c1 = self.board[high_src][0]
                                    else:
                                        c1 = (self.board[s1_highest][0] + 1) if t1 == s1_highest else self.board[s1_highest][0]

                                    active_positions -= {s1_highest}
                                    move_s1 = (s1_highest, clamp(s1_highest + r))

                                    if c1 == 1:
                                        s2_highest = highest(player, [s for s in active_positions if comp1(player, s, r)])
                                        plays.add(out_of_home_move + (move1,) + (move_s1, ))

                                        if s2_highest is not None:
                                            if self.board[s2_highest][1] != player:
                                                c2 = 1
                                            else:
                                                c2 = (self.board[s2_highest][0] + 1) if t1 == s2_highest else self.board[s2_highest][0]
                                            active_positions -= {s2_highest}
                                            move_s2 = (s2_highest, clamp(s2_highest + r))

                                            if c2 >= 1:
                                                plays.add(out_of_home_move + (move1,) + (move_s1,) + (move_s2, ))

                                    elif c1 >= 2:
                                        plays.add(out_of_home_move + (move1, ) + (move_s1, ) + (move_s1, ))

                            elif self.is_valid(player, t2):

                                if comp3(player, s1, t2):
                                    active_positions.add(t2)
                                    s1_highest = highest(player, [s for s in active_positions if comp1(player, s, r)])

                                    if s1_highest is not None:
                                        if self.board[s1_highest][1] != player:
                                            c1 = self.board[high_src][0]
                                        else:
                                            c1 = (self.board[s1_highest][0] + 1) if t2 == s1_highest else self.board[s1_highest][0]
                                        active_positions -= {s1_highest}
                                        move_s1 = (s1_highest, clamp(s1_highest + r))

                                        if c1 >= 1:
                                            plays.add(out_of_home_move + (move1, ) + (move2,) + (move_s1, ))

                        elif self.board[high_src][0] == 2:
                            if comp3(player, s1, t1):
                                active_positions.add(t1)
                                s1_highest = highest(player, [s for s in active_positions if comp1(player, s, r)])

                                if s1_highest is not None:
                                    if self.board[s1_highest][1] != player:
                                        c1 = self.board[high_src][0]
                                    else:
                                        c1 = (self.board[s1_highest][0] + 1) if t1 == s1_highest else self.board[s1_highest][0]
                                    move_s1 = (s1_highest, clamp(s1_highest + r))

                                    if c1 >= 1:
                                        active_positions -= {s1_highest}
                                        plays.add(out_of_home_move + (move1,) + (move1,) + (move_s1, ))

                if dice_used == 2:
                    high_src = list(higher_src)[0]
                    active_positions -= {high_src}

                    t1 = high_src + r
                    t2 = t1 + r

                    move1 = (high_src, clamp(t1))

                    if self.is_valid(player, t1):

                        if self.board[high_src][0] == 1:

                            if comp3(player, s1, t1):
                                active_positions.add(t1)
                                s1_highest = highest(player, [s for s in active_positions if comp1(player, s, r)])

                                if s1_highest is not None:
                                    if self.board[s1_highest][1] != player:
                                        c1 = self.board[high_src][0]
                                    else:
                                        c1 = (self.board[s1_highest][0] + 1) if t1 == s1_highest else self.board[s1_highest][0]

                                    active_positions -= {s1_highest}
                                    move_s1 = (s1_highest, clamp(s1_highest + r))

                                    if c1 >= 1:
                                        plays.add(out_of_home_move + (move1,) + (move_s1,))
            if len(higher_src) == 2:
                if dice_used == 0:

                    high_src1 = list(higher_src)[0]
                    high_src2 = list(higher_src)[1]

                    if (self.board[high_src1][0] + self.board[high_src2][0]) <= 3:

                        active_positions -= {high_src1}
                        active_positions -= {high_src2}

                        t11 = high_src1 + r
                        t21 = t11 + r

                        t12 = high_src2 + r
                        t22 = t12 + r

                        move11 = (high_src1, clamp(t11))
                        move21 = (t11, clamp(t21))

                        move12 = (high_src2, clamp(t12))
                        move22 = (t12, clamp(t22))

                        if self.is_valid(player, t11) and self.is_valid(player, t12):

                            if comp3(player, s1, t11) and comp3(player, s1, t12):
                                active_positions.add(t11)
                                active_positions.add(t12)
                                s1_best = highest(player, [s for s in active_positions if comp1(player, s, r)])

                                if s1_best is not None:
                                    if self.board[s1_best][1] != player:
                                        c1 = 2 if s1_best == t11 and s1_best == t12 else 1
                                    else:
                                        c1 = (self.board[s1_best][0] + 1) if t11 == s1_best else self.board[s1_best][0]
                                        c1 = (c1 + 1) if t12 == s1_best else c1

                                    active_positions -= {s1_best}
                                    move_s1 = (s1_best, clamp(s1_best + r))

                                    if self.board[high_src1][0] == 1 and self.board[high_src2][0] == 1:

                                        if c1 == 1:
                                            s2_best = highest(player, [s for s in active_positions if comp1(player, s, r)])
                                            plays.add((move11, move12, move_s1))

                                            if s2_best is not None:
                                                move_s2 = (s2_best, clamp(s2_best + r))
                                                plays.add((move11, move12, move_s1, move_s2))

                                        elif c1 >= 2:
                                            plays.add((move11, move12, move_s1, move_s1))

                                    elif self.board[high_src1][0] == 2 and self.board[high_src2][0] == 1:
                                        plays.add((move11, move11, move12, move_s1))

                                    elif self.board[high_src1][0] == 1 and self.board[high_src2][0] == 2:
                                        plays.add((move12, move12, move11, move_s1))

                            elif comp3(player, s1, t11) and self.board[high_src2][0] < 2:

                                if self.is_valid(player, t12) and comp3(player, s1, t22) and self.board[high_src1][0] < 2:

                                    if self.is_valid(player, t22):
                                        active_positions.add(t11)
                                        active_positions.add(t22)
                                        s1_best = highest(player, [s for s in active_positions if comp1(player, s, r)])

                                        if s1_best is not None:
                                            move_s1 = (s1_best, clamp(s1_best + r))
                                            plays.add((move11, move12, move22, move_s1))

                            elif comp3(player, s1, t12) and self.board[high_src1][0] < 2:

                                if self.is_valid(player, t11) and comp3(player, s1, t21) and self.board[high_src2][0] < 2:

                                    if self.is_valid(player, t21):
                                        active_positions.add(t12)
                                        active_positions.add(t21)
                                        s1_best = highest(player, [s for s in active_positions if comp1(player, s, r)])

                                        if s1_best is not None:
                                            move_s1 = (s1_best, clamp(s1_best + r))
                                            plays.add((move12, move11, move21, move_s1))

                if dice_used == 1:

                    high_src1 = list(higher_src)[0]
                    high_src2 = list(higher_src)[1]

                    if (self.board[high_src1][0] + self.board[high_src2][0]) <= 2:

                        active_positions -= {high_src1}
                        active_positions -= {high_src2}

                        t11 = high_src1 + r

                        t12 = high_src2 + r

                        move11 = (high_src1, clamp(t11))
                        move12 = (high_src2, clamp(t12))

                        if self.is_valid(player, t11) and self.is_valid(player, t12):

                            if comp3(player, s1, t11) and comp3(player, s1, t12):
                                active_positions.add(t11)
                                active_positions.add(t12)
                                s1_best = highest(player, [s for s in active_positions if comp1(player, s, r)])

                                if s1_best is not None:
                                    if self.board[s1_best][1] != player:
                                        c1 = 2 if s1_best == t11 and s1_best == t12 else 1
                                    else:
                                        c1 = (self.board[s1_best][0] + 1) if t11 == s1_best else self.board[s1_best][0]
                                        c1 = (c1 + 1) if t12 == s1_best else c1

                                    active_positions -= {s1_best}
                                    move_s1 = (s1_best, clamp(s1_best + r))

                                    if self.board[high_src1][0] == 1 and self.board[high_src2][0] == 1:

                                        if c1 >= 1:
                                            plays.add(out_of_home_move + (move11,) + (move12,) + (move_s1, ))
            if len(higher_src) == 3:
                if dice_used == 0:
                    high_src1 = list(higher_src)[0]
                    high_src2 = list(higher_src)[1]
                    high_src3 = list(higher_src)[2]

                    t1 = high_src1 + r
                    t2 = high_src2 + r
                    t3 = high_src3 + r

                    move1 = (high_src1, clamp(t1))
                    move2 = (high_src2, clamp(t2))
                    move3 = (high_src3, clamp(t3))

                    if (self.board[high_src1][0] + self.board[high_src2][0] + self.board[high_src3][0]) <= 3:

                        if self.is_valid(player, t1) and self.is_valid(player, t2) and self.is_valid(player, t3):

                            if comp3(player, s1, t1) and comp3(player, s1, t2) and comp3(player, s1, t3):
                                active_positions.add(t1)
                                active_positions.add(t2)
                                active_positions.add(t3)
                                s1_best = highest(player, [s for s in active_positions if comp1(player, s, r)])

                                if s1_best is not None:
                                    move_s1 = (s1_best, clamp(s1_best + r))
                                    plays.add((move1, move2, move3, move_s1))

        self.restore_state(old_state)
        return plays

    # =================================================================================
    # BAR PLAYS =======================================================================
    # =================================================================================
    def get_single_moves(self, player, roll, other_move_target=None, player_src=None):
        if player_src is not None:
            moves = {(s, s + roll) for s in player_src if self.is_valid(player, s + roll)}
        else:
            moves = {(s, s + roll) for s in list(self.players_positions[player]) if self.is_valid(player, s + roll)}

        if other_move_target is not None and self.is_valid(player, other_move_target + roll):
            moves.add((other_move_target, other_move_target + roll))

        return moves

    def get_double_moves(self, player, roll, single_moves):
        moves = set()
        if len(single_moves) > 0:
            moves = {((s, t), (t, t + roll)) for (s, t) in single_moves if self.is_valid(player, t + roll)}
            moves.update(list(itertools.combinations(single_moves, 2)))
            moves.update([((s, t), (s, t)) for (s, t) in single_moves if self.board[s][0] >= 2])
        return moves

    def get_triple_moves(self, player, roll, double_moves):
        moves = set()
        reverse = player == WHITE
        if len(double_moves) > 0:
            for (m1, m2) in double_moves:
                s1, t1 = m1
                s2, t2 = m2

                if self.is_valid(player, t1 + roll) and ((t1 != s2) or (self.board[t1][0] > 0 and self.board[t1][1] == player)):
                    moves.add((m1, (t1, t1 + roll), m2))

                if self.is_valid(player, t2 + roll) and (t2 != s1):
                    moves.add((m1, m2, (t2, t2 + roll)))

                for s in self.players_positions[player]:
                    t = s + roll
                    if self.is_valid(player, t):
                        if (self.board[s][0] > 2 and ((s, t) == m1 or (s, t) == m2)) or ((s, t) != m1 and (s, t) != m2):
                            moves.add((m1, m2, (s, t)))

                        if (m1 != m2) and self.board[s][0] > 1 and ((s, t) == m1 or (s, t) == m2):
                            moves.add((m1, m2, (s, t)))

        moves = {tuple(sorted(play, reverse=reverse)) for play in moves}
        return moves

    def get_bar_plays(self, player, roll):
        plays = set()
        r1, r2 = roll

        t1 = NUM_POINTS - abs(r1) if player == WHITE else abs(r1) - 1
        t2 = NUM_POINTS - abs(r2) if player == WHITE else abs(r2) - 1

        if self.can_move_to(player, t1) and self.can_move_to(player, t2):
            # "If you can play one number but not both, then you must play the higher one."
            t = min(t1, t2) if player == WHITE else max(t1, t2)
            plays.add(((BAR, t),))

        else:
            if self.can_move_to(player, t1):
                plays.add(((BAR, t1),))

            if self.can_move_to(player, t2):
                plays.add(((BAR, t2),))

        if self.bar[player] >= 2:
            if self.can_move_to(player, t1) and self.can_move_to(player, t2):
                plays.add(((BAR, t1), (BAR, t2)))

        else:
            if self.can_move_to(player, t1):
                plays.update([((BAR, t1), move) for move in self.get_single_moves(player, r2, other_move_target=t1)])

            if self.can_move_to(player, t2):
                plays.update([((BAR, t2), move) for move in self.get_single_moves(player, r1, other_move_target=t2)])

        return plays

    # BAR PLAYS - DOUBLE ==============================================================
    def get_bar_plays_double(self, player, roll):
        plays = set()

        r = roll[0]
        t = NUM_POINTS - abs(r) if player == WHITE else abs(r) - 1

        if self.is_valid(player, t):
            old_state = self.save_state()
            move = (BAR, t)

            if self.board[t][1] == player:
                self.board[t] = (self.board[t][0] + self.bar[player], player)
            else:
                self.board[t] = (self.bar[player], player)

            self.players_positions = self.get_players_positions()

            if self.bar[player] == 1:
                single_moves = self.get_single_moves(player, roll=r, other_move_target=t)
                double_moves = self.get_double_moves(player, roll=r, single_moves=single_moves)
                triple_moves = self.get_triple_moves(player, roll=r, double_moves=double_moves)

                plays.add((move,))
                plays.update([(move, single) for single in single_moves])
                plays.update([(move, double[0], double[1]) for double in double_moves])
                plays.update([(move, triple[0], triple[1], triple[2]) for triple in triple_moves])

            elif self.bar[player] == 2:
                single_moves = self.get_single_moves(player, roll=r, other_move_target=t)
                double_moves = self.get_double_moves(player, roll=r, single_moves=single_moves)

                plays.add((move, move))
                plays.update([(move, move, single) for single in single_moves])
                plays.update([(move, move, double[0], double[1]) for double in double_moves])

            elif self.bar[player] == 3:
                single_moves = self.get_single_moves(player, roll=r, other_move_target=t)

                plays.add((move, move, move))
                plays.update([(move, move, move, single) for single in single_moves])

            elif self.bar[player] >= 4:
                plays.add((move, move, move, move))

            self.restore_state(old_state)

        return plays

    def render(self):
        points = [p[0] for p in self.board]
        bottom_board = points[:12][::-1]
        top_board = points[12:]

        colors = [TOKEN[WHITE] if p[1] == WHITE else TOKEN[BLACK] for p in self.board]
        bottom_checkers_color = colors[:12][::-1]
        top_checkers_color = colors[12:]

        assert len(bottom_board) + len(top_board) == 24
        assert len(bottom_checkers_color) + len(top_checkers_color) == 24

        print("| 12 | 13 | 14 | 15 | 16 | 17 | BAR | 18 | 19 | 20 | 21 | 22 | 23 | OFF |")
        print(f"|--------Outer Board----------|     |-------P={TOKEN[BLACK]} Home Board--------|     |")
        self.print_half_board(top_board, top_checkers_color, WHITE, reversed_=1)
        print("|-----------------------------|     |-----------------------------|     |")
        self.print_half_board(bottom_board, bottom_checkers_color, BLACK, reversed_=-1)
        print(f"|--------Outer Board----------|     |-------P={TOKEN[WHITE]} Home Board--------|     |")
        print("| 11 | 10 |  9 |  8 |  7 |  6 | BAR |  5 |  4 |  3 |  2 |  1 |  0 | OFF |\n")

    def print_half_board(self, half_board, checkers_color, player, reversed_=-1):
        token = TOKEN[player]
        max_length = max(max(half_board), max([self.bar[player], self.off[player]]))
        for i in range(max_length)[::reversed_]:
            row = [str(checkers_color[k]) if half_board[k] > i else " " for k in range(len(half_board))]
            bar = [f"{token} " if self.bar[player] > i else "  "]
            off = [f"{token} " if self.off[player] > i else "  "]
            row = row[:6] + bar + row[6:] + off
            print("|  " + " |  ".join(row) + " |")

    def get_players_positions(self):
        player_positions = [[], []]
        for key, (checkers, player) in enumerate(self.board):
            if player is not None and key not in player_positions:
                player_positions[player].append(key)
        return player_positions

    def get_valid_plays(self, player, roll):
        valid_plays = set()
        top_valid_plays = set()

        normal_plays = set()
        bear_off_plays = set()
        bar_plays = set()
        reverse = player == WHITE

        roll = (roll[0], roll[0], roll[0], roll[0]) if roll[0] == roll[1] else roll

        if self.bar[player]:
            bar_plays = self.get_bar_plays(player, roll) if len(roll) <= 2 else self.get_bar_plays_double(player, roll)
        else:
            if self.could_bear_off(player, roll):
                bear_off_plays = self.get_bear_off_plays(player, roll) if len(roll) <= 2 else self.get_bear_off_play_double(player, roll)
            normal_plays = self.get_normal_plays(player, roll) if len(roll) <= 2 else self.get_normal_plays_double(player, roll)

        valid_plays.update(normal_plays)
        valid_plays.update(bear_off_plays)

        valid_plays = {tuple(sorted(play, reverse=reverse)) for play in valid_plays}

        valid_plays.update(bar_plays)

        if len(valid_plays) > 0:
            max_length_move = len(max(valid_plays, key=len))  # select the plays that use the most number of dice
            top_valid_plays = {play for play in valid_plays if len(play) == max_length_move}

        return top_valid_plays

    def execute_play(self, current_player, action):
        if action:
            tmp = self.board[:]
            for move in action:
                if move:
                    src, target = move
                    if 0 <= target < NUM_POINTS:
                        checkers_on_target, player_on_target = self.board[target]

                        if current_player != player_on_target and player_on_target is not None:
                            self.bar[player_on_target] += 1
                            checkers_on_target = 0

                        if src == BAR:
                            self.bar[current_player] -= 1
                            self.board[target] = (checkers_on_target + 1, current_player)
                        else:
                            checkers_on_src, player_on_src = self.board[src]
                            checkers_on_src -= 1

                            if checkers_on_src < 1:
                                player_on_src = None

                            self.board[src] = (checkers_on_src, player_on_src)
                            self.board[target] = (checkers_on_target + 1, current_player)
                    else:  # OFF BOARD MOVE
                        checkers_on_src, player_on_src = self.board[src]
                        checkers_on_src -= 1

                        if checkers_on_src < 1:
                            player_on_src = None

                        self.board[src] = (checkers_on_src, player_on_src)
                        self.off[current_player] += 1

                    self.players_positions = self.get_players_positions()

            assert_board(action=action, board=self.board, bar=self.bar, off=self.off, game=self, old_board=tmp)

    def save_state(self):
        return BackgammonState(board=self.board[:], bar=self.bar[:], off=self.off[:], players_positions=self.players_positions[:])

    def restore_state(self, old_state):
        self.board, self.bar, self.off, self.players_positions = old_state.board[:], old_state.bar[:], old_state.off[:], old_state.players_positions[:]
        self.state = BackgammonState(board=self.board, bar=self.bar, off=self.off, players_positions=self.players_positions)

    def get_winner(self):
        if self.off[WHITE] == 15:
            return WHITE
        elif self.off[BLACK] == 15:
            return BLACK
        return None

    def get_opponent(self, player):
        return BLACK if player == WHITE else WHITE

    def get_board_features(self, current_player):
        """
        - encode each point (24) with 4 units => 4 * 24 = 96
        - for each player => 96 * 2 = 192
        - 2 units indicating who is the current player
        - 2 units for white and black bar checkers
        - 2 units for white and block off checkers
        - tot = 192 + 2 + 2 + 2 = 198
        """
        features_vector = []
        for p in [WHITE, BLACK]:
            for point in range(0, NUM_POINTS):
                checkers, player = self.board[point]
                if player == p and checkers > 0:
                    if checkers == 1:
                        features_vector += [1.0, 0.0, 0.0, 0.0]
                    elif checkers == 2:
                        features_vector += [1.0, 1.0, 0.0, 0.0]
                    elif checkers >= 3:
                        features_vector += [1.0, 1.0, 1.0, (checkers - 3.0) / 2.0]
                else:
                    features_vector += [0.0, 0.0, 0.0, 0.0]

            features_vector += [self.bar[p] / 2.0, self.off[p] / 15.0]

        if current_player == WHITE:
            # features_vector += [0.0, 1.0]
            features_vector += [1.0, 0.0]
        else:
            # features_vector += [1.0, 0.0]
            features_vector += [0.0, 1.0]
        assert len(features_vector) == 198, print(f"Should be 198 instead of {len(features_vector)}")
        return features_vector


def assert_board(action, board, bar, off, game=None, old_board=None):
    sum_white = 0
    sum_black = 0
    for (checkers, player) in board:
        if player == WHITE:
            sum_white += checkers
        elif player == BLACK:
            sum_black += checkers

    assert 0 <= sum_white <= 15 and 0 <= sum_black <= 15, print_assert(game, sum_white, sum_black, bar, off, action, old_board)
    assert bar[WHITE] < 16 and bar[BLACK] < 16, print_assert(game, sum_white, sum_black, bar, off, action, old_board)
    assert off[WHITE] < 16 and off[BLACK] < 16, print_assert(game, sum_white, sum_black, bar, off, action, old_board)
    assert sum_white + bar[WHITE] + off[WHITE] == 15, print_assert(game, sum_white, sum_black, bar, off, action, old_board)
    assert sum_black + bar[BLACK] + off[BLACK] == 15, print_assert(game, sum_white, sum_black, bar, off, action, old_board)


def print_assert(game, sum_white, sum_black, bar, off, action, old_board):
    if game is not None:
        game.render()

    if old_board is not None:
        game.board = old_board
        game.render()
    print(f"sum_white={sum_white} | sum_black={sum_black} | bar={bar} | off={off} | action={action}")
