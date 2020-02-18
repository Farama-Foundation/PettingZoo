import pyglet
from pyglet import gl
import numpy as np
from collections import namedtuple
from gym_backgammon.envs.backgammon import WHITE, BLACK, NUM_POINTS
import os
import platform
Coords = namedtuple('Coords', ['x', 'y'])

SCALING = 2 if platform.system() == 'Darwin' else 1

class Viewer(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.window = pyglet.window.Window(width=width, height=height, display=None)

        pyglet.resource.path = [os.path.dirname(__file__) + '/resources']
        pyglet.resource.reindex()

        empty_board_image = pyglet.resource.image("board.png")
        empty_board_image.width = width
        empty_board_image.height = height

        self.empty_board_image = empty_board_image

        # CHECKERS
        self.checker_diameter = self.width / 15  # 40

        self.checkers = {
            WHITE: {i: pyglet.resource.image("white_{}.png".format(i)) for i in range(1, 16)},
            BLACK: {i: pyglet.resource.image("black_{}.png".format(i)) for i in range(1, 16)}
        }

        coords = {}
        shifts = [2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13, 14]

        for i in range(NUM_POINTS):
            index = 23 - i if 11 < i <= 23 else i

            if i < 12:
                coords[i] = Coords(x=width - (shifts[index] * self.checker_diameter), y=self.checker_diameter)
            else:
                coords[i] = Coords(x=width - (shifts[index] * self.checker_diameter), y=height - self.checker_diameter)

        coords['bar_{}'.format(WHITE)] = Coords(x=width - (8 * self.checker_diameter), y=height - self.checker_diameter)
        coords['bar_{}'.format(BLACK)] = Coords(x=width - (8 * self.checker_diameter), y=self.checker_diameter)

        coords['off_{}'.format(WHITE)] = Coords(x=width - self.checker_diameter, y=self.checker_diameter)
        coords['off_{}'.format(BLACK)] = Coords(x=width - self.checker_diameter, y=height - self.checker_diameter)

        self.points_coord = coords

        # remove
        self.counter = 0

        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

    def close(self):
        self.window.close()

    def render(self, board, bar, off, state_w, state_h, return_rgb_array=True):
        gl.glClearColor(1, 1, 1, 1)

        self.window.switch_to()
        self.window.dispatch_events()
        self.window.clear()

        batch = pyglet.graphics.Batch()
        sprites = []

        for point, (checkers, player) in enumerate(board):

            if player is not None:
                assert player in [WHITE, BLACK], print("Should be WHITE (0) or BLACK (1), not {}".format(player))
                assert point in self.points_coord, print("Should be 0 <= point < 24, not {}".format(point))
                assert 0 <= checkers <= 15, print("Should be 0 <= checkers <= 15, not {}".format(checkers))

                c = self.points_coord[point]
                img = self.checkers[player][checkers]
                checkers = 5 if checkers > 5 else checkers
                img.width = self.checker_diameter
                img.height = self.checker_diameter * checkers

                if point < 12:
                    s = pyglet.sprite.Sprite(img=img, x=c.x, y=c.y, batch=batch)
                else:
                    s = pyglet.sprite.Sprite(img=img, x=c.x + self.checker_diameter, y=c.y - (checkers * self.checker_diameter) + img.height, batch=batch)
                    s.rotation = 180

                sprites.append(s)

        for player in [WHITE, BLACK]:
            # BAR
            checkers = bar[player]
            if checkers > 0:
                c = self.points_coord['bar_{}'.format(player)]

                img = self.checkers[player][checkers]
                checkers = 5 if checkers > 5 else checkers
                img.width = self.checker_diameter
                img.height = self.checker_diameter * checkers

                if player == BLACK:
                    s = sprites.append(pyglet.sprite.Sprite(img=img, x=c.x, y=c.y, batch=batch))
                else:
                    s = pyglet.sprite.Sprite(img=img, x=c.x + self.checker_diameter, y=c.y - (checkers * self.checker_diameter) + img.height, batch=batch)
                    s.rotation = 180
                sprites.append(s)

            # OFF
            checkers = off[player]
            if checkers > 0:

                c = self.points_coord['off_{}'.format(player)]
                img = self.checkers[player][checkers]
                checkers = 5 if checkers > 5 else checkers
                img.width = self.checker_diameter
                img.height = self.checker_diameter * checkers

                if player == WHITE:
                    s = sprites.append(pyglet.sprite.Sprite(img=img, x=c.x, y=c.y, batch=batch))
                else:
                    s = pyglet.sprite.Sprite(img=img, x=c.x + self.checker_diameter, y=c.y - (checkers * self.checker_diameter) + img.height, batch=batch)
                    s.rotation = 180

                sprites.append(s)

        gl.glViewport(0, 0, state_w, state_h)

        pyglet.sprite.Sprite(img=self.empty_board_image, batch=None).draw()
        batch.draw()

        arr = None

        if return_rgb_array:
            buffer = pyglet.image.get_buffer_manager().get_color_buffer()
            image_data = buffer.get_image_data()
            arr = np.fromstring(image_data.data, dtype=np.uint8, sep='')
            arr = arr.reshape((state_h, state_w, 4))
            arr = arr[::-1, :, 0:3]

        gl.glViewport(0, 0, SCALING * self.window.width, SCALING * self.window.height)
        pyglet.sprite.Sprite(img=self.empty_board_image, batch=None).draw()
        batch.draw()

        self.window.flip()

        return arr
