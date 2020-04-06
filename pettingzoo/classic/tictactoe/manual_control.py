import pygame
from pygame.locals import QUIT, MOUSEBUTTONUP

from .board import Board
from .board_ui import Board as BoardUI


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
                done = True
            elif event.type == MOUSEBUTTONUP:
                x, y = event.pos
                action, square = board_ui.get_square_at_pixel(x, y)

                # check if its a valid action
                if env.board.squares[action] == 0:
                    if env.agent_selection == env.agents[0]:
                        square.mark_x()
                    else:
                        square.mark_o()

                    env.step(action)
                    done = all(env.dones.values())

                    if done:
                        winner = env.board.check_for_winner()
                        board_ui.display_game_over(winner)
                        break
                else:
                    print("Invalid move")

        pygame.display.update()
        clock.tick(30)

    pygame.time.wait(2000)
    board_ui.close()
