import pygame, sys
from pygame.locals import QUIT, MOUSEBUTTONUP

from .board import Board
from .tictactoe_utils import Board as BoardUI


def manual_control(**kwargs):
    from .tictactoe import env as _env
    env = _env(**kwargs)

    pygame.init()
    clock = pygame.time.Clock()

    # BoardUI to draw the actual board
    board_ui = BoardUI()

    done = all(env.dones.values())
    
    while not done:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONUP:
                x, y = event.pos

                board_ui.process_click(x, y, env.agent_selection)
                print("Board: " + str([square.state for square in board.squares]))
                print("Winner: " + str(board.check_for_winner()))
    
        pygame.display.update()
        clock.tick(30)
