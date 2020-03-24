import pygame
import itertools


WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)


class Square(object):

    def __init__(self, x, y, size, board):
        self.size = size
        self.line_width = int(self.size / 40) if self.size > 40 else 1
        self.radius = (self.size / 2) - (self.size / 8)
        self.rect = pygame.Rect(x, y, size, size)
        self.board = board

    def mark_x(self):
        pygame.draw.line(self.board.surface, RED, (self.rect.centerx - self.radius, self.rect.centery - self.radius), (self.rect.centerx + self.radius, self.rect.centery + self.radius), self.line_width)
        pygame.draw.line(self.board.surface, RED, (self.rect.centerx - self.radius, self.rect.centery + self.radius), (self.rect.centerx + self.radius, self.rect.centery - self.radius), self.line_width)

    def mark_o(self):
        pygame.draw.circle(self.board.surface, BLUE, (self.rect.centerx, self.rect.centery), self.radius, self.line_width)


class Board(object):

    def __init__(self, grid_size=3, square_size=100, border=50, line_width=10):
        self.grid_size = grid_size
        self.square_size = square_size
        self.border = border
        self.line_width = line_width
        surface_size = (self.grid_size * self.square_size) + (self.border * 2) + (self.line_width * (self.grid_size - 1))
        self.surface = pygame.display.set_mode((surface_size, surface_size), 0, 32)
        self.game_over = False
        self.setup()

    def setup(self):
        pygame.display.set_caption('Tic Tac Toe')
        self.surface.fill(WHITE)
        self.draw_lines()
        self.initialize_squares()

    def draw_lines(self):
        for i in range(1, self.grid_size):
            start_position = ((self.square_size * i) + (self.line_width * (i - 1))) + self.border
            width = self.surface.get_width() - (2 * self.border)
            pygame.draw.rect(self.surface, BLACK, (start_position, self.border, self.line_width, width))
            pygame.draw.rect(self.surface, BLACK, (self.border, start_position, width, self.line_width))

    def initialize_squares(self):
        self.squares = []

        top_left_numbers = []
        for i in range(0, self.grid_size):
            num = ((i * self.square_size) + self.border + (i * self.line_width))
            top_left_numbers.append(num)

        square_coordinates = list(itertools.product(top_left_numbers, repeat=2))
        for x, y in square_coordinates:
            self.squares.append(Square(x, y, self.square_size, self))

    def get_square_at_pixel(self, x, y):
        for index, square in enumerate(self.squares):
            if square.rect.collidepoint(x, y):
                return (index, square)
        return None

    def display_game_over(self, winner):
        surface_size = self.surface.get_height()
        font = pygame.font.Font('freesansbold.ttf', int(surface_size / 8))
        if winner:
            text = 'Player %s won!' % winner
        else:
            text = 'Draw!'
        text = font.render(text, True, BLACK, WHITE)
        rect = text.get_rect()
        rect.center = (surface_size / 2, surface_size / 2)
        self.surface.blit(text, rect)

    def close(self):
        pygame.event.pump()
        pygame.display.quit()
