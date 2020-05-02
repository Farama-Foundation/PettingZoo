from .chess import chess_env
from .rps import rps
from .rpsls import rpsls as rpsls_v0
from .connect_four import connect_four as connect_four_v0
from .tictactoe import tictactoe as tictactoe_v0
from .leduc_holdem import leduc_holdem as leduc_holdem_v0
from .mahjong import mahjong as mahjong_v0
from .texas_holdem import texas_holdem as texas_holdem_v0
from .texas_holdem_no_limit import texas_holdem_no_limit as texas_holdem_no_limit_v0
from .uno import uno as uno_v0
from .dou_dizhu import dou_dizhu as dou_dizhu_v0
from .gin_rummy import gin_rummy as gin_rummy_v0
from .go import go_env as go_v0
from pettingzoo.utils.wrappers import TerminateIllegalWrapper,TerminateNaNWrapper,NanNoOpWrapper, \
                                AssertOutOfBoundsWrapper,OrderEnforcingWrapper
class chess_v0:
    @staticmethod
    def env(**kwargs):
        env = chess_env.env(**kwargs)
        env = TerminateIllegalWrapper(env,illegal_reward=-1)
        env = AssertOutOfBoundsWrapper(env)
        env = TerminateNaNWrapper(env)
        env = OrderEnforcingWrapper(env)
        return env

class rps_v0:
    @staticmethod
    def env(**kwargs):
        env = rps.env(**kwargs)
        env = AssertOutOfBoundsWrapper(env)
        env = TerminateNaNWrapper(env)
        env = OrderEnforcingWrapper(env)
        return env
