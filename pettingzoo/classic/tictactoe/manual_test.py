import pygame, sys
from pygame.locals import QUIT, MOUSEBUTTONUP

from .tictactoe_utils import Board

pygame.init()
clock = pygame.time.Clock()
board = Board()

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == MOUSEBUTTONUP:
            x, y = event.pos
            board.process_click(x, y)
            print("Board: " + str([square.state for square in board.squares]))
            print("Winner: " + str(board.check_for_winner()))

    pygame.display.update()
    clock.tick(30)
