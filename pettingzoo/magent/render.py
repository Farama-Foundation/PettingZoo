import math
import magent
import numpy as np

animation_total = 2
animation_stop = 0
background_rgb = (255, 255, 255)
attack_line_rgb = (0, 0, 0)
attack_dot_rgb = (0, 0, 0)
attack_dot_size = 0.3
text_rgb = (0, 0, 0)
text_size = 16
text_spacing = 3
banner_size = 20
banner_spacing = 3
bigscreen_size = 72
bigscreen_spacing = 0
grid_rgba = ((0, 0, 0), 30)
grid_size = 8


def draw_line(surface, color, a, b):
    import pygame
    pygame.draw.line(
        surface, color,
        (int(round(a[0])), int(round(a[1]))),
        (int(round(b[0])), int(round(b[1])))
    )


def draw_rect(surface, color, a, w, h):
    import pygame
    pygame.draw.rect(surface, color, pygame.Rect(*map(int, (
        round(a[0]), round(a[1]),
        round(w + a[0] - round(a[0])),
        round(h + a[1] - round(a[1]))))))


def draw_rect_matrix(matrix, color, a, w, h, resolution):
    x, y, w, h = map(int, (round(a[0]), round(a[1]), round(w + a[0] - round(a[0])), round(h + a[1] - round(a[1]))))
    matrix[max(x, 0):min(x + w, resolution[0]), max(y, 0):min(h + y, resolution[1]), :] = color


def draw_line_matrix(matrix, color, a, b, resolution):
    a = (min(max(0, a[0]), resolution[0] - 1), min(max(0, a[1]), resolution[1] - 1))
    b = (min(max(0, b[0]), resolution[0] - 1), min(max(0, b[1]), resolution[1] - 1))
    a = map(int, (round(a[0]), round(a[1])))
    b = map(int, (round(b[0]), round(b[1])))
    if a[0] == b[0]:
        if a[1] > b[1]:
            matrix[a[0], b[1]:a[1] + 1] = color
        else:
            matrix[a[0], a[1]:b[1] + 1] = color
    elif a[1] == b[1]:
        if a[0] > b[0]:
            matrix[b[0]:a[0] + 1, a[1]] = color
        else:
            matrix[a[0]:b[0] + 1, a[1]] = color
    else:
        raise NotImplementedError


class Renderer:
    def __init__(self, env, map_size, mode):
        import pygame
        self.env = env
        self.mode = mode
        self.handles = self.env.get_handles()

        base_resolution = (map_size * 8, map_size * 8 + 15)
        if mode == "human":
            pygame.init()
            pygame.display.init()
            infoObject = pygame.display.Info()
            screen_size = (infoObject.current_w - 50, infoObject.current_h - 50)
            self.resolution = resolution = np.min([screen_size, base_resolution], axis=0)
            self.display = pygame.display.set_mode(resolution, pygame.DOUBLEBUF, 0)
            canvas_resolution = (resolution[0], resolution[1])
            self.canvas = pygame.Surface(canvas_resolution)
            pygame.display.set_caption('MAgent Renderer Window')
        elif mode == "rgb_array":
            pygame.font.init()
            self.resolution = base_resolution
            self.display = pygame.Surface(base_resolution)
            canvas_resolution = (base_resolution[0], base_resolution[1])
            self.canvas = pygame.Surface(canvas_resolution)

        self.text_formatter = pygame.font.SysFont(None, text_size, True)
        self.banner_formatter = pygame.font.SysFont(None, banner_size, True)
        self.bigscreen_formatter = pygame.font.SysFont(None, bigscreen_size, True)

        self.map_size = (map_size, map_size)

        self.frame_id = 0

        self.old_data = None
        self.new_data = None

        self.need_static_update = True
        self.animation_progress = 0

    def get_banners(self, frame_id, resolution):
        groups = self.env._get_groups_info()

        def form_txt(index):
            handle = self.handles[index]
            color = tuple([int(a) for a in groups[index][2:]])
            return '{}'.format(np.sum(self.env.get_alive(handle).astype(np.int32))), color
        if len(self.handles) == 1:
            result = [(form_txt(0), )]
        if len(self.handles) == 2:
            vs = ' vs ', (0, 0, 0)
            result = [(form_txt(0), vs, form_txt(1))]
        elif len(self.handles) == 4:
            vs = ' vs ', (0, 0, 0)
            comma = ', ', (0, 0, 0)
            result = [(form_txt(0), comma, form_txt(1), vs, form_txt(2), comma, form_txt(3))]
        else:
            raise RuntimeError("bad number of handles")

        return result

    def close(self):
        import pygame
        pygame.display.quit()
        pygame.quit()

    def render(self, mode):
        import os
        os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
        import pygame

        env = self.env
        self.groups = env._get_groups_info()
        resolution = self.resolution

        grid_map = np.zeros((resolution[0], resolution[1], 3), dtype=np.int16)
        view_position = [self.map_size[0] / 2 * grid_size - resolution[0] / 2,
                         self.map_size[1] / 2 * grid_size - resolution[1] / 2]
        groups = self.groups
        banner_formatter = self.banner_formatter
        status = True
        triggered = False
        # x_range: which vertical gridlines should be shown on the display
        # y_range: which horizontal gridlines should be shown on the display
        x_range = (
            max(0, int(math.floor(max(0, view_position[0]) / grid_size))),
            min(self.map_size[0], int(math.ceil(max(0, view_position[0] + resolution[0]) / grid_size)))
        )

        y_range = (
            max(0, int(math.floor(max(0, view_position[1]) / grid_size))),
            min(self.map_size[1], int(math.ceil(max(0, view_position[1] + resolution[1]) / grid_size)))
        )

        self.canvas.fill(background_rgb)
        self.display.fill(background_rgb)

        if self.need_static_update or True:
            grids = pygame.Surface(resolution)
            grids.fill(background_rgb)

        if self.new_data is None or self.animation_progress > animation_total + animation_stop:
            pos, event = env._get_render_info(x_range, y_range)
            buffered_new_data = pos, event

            if buffered_new_data is None:
                buffered_new_data = self.new_data
            self.old_data = self.new_data
            self.new_data = buffered_new_data
            self.animation_progress = 0

        if self.new_data is not None:
            if self.old_data is None and self.animation_progress == 0:
                self.animation_progress = animation_total

            if self.need_static_update or True:
                pygame.pixelcopy.surface_to_array(grid_map, self.canvas)
                for wall in env._get_walls_info():
                    x, y = wall[0], wall[1]
                    if x >= x_range[0] and x <= x_range[1] and y >= y_range[0] and y <= y_range[1]:
                        draw_rect_matrix(grid_map, (127, 127, 127),
                                         (x * grid_size - view_position[0], y * grid_size - view_position[1]),
                                         grid_size, grid_size, resolution)
            pygame.pixelcopy.array_to_surface(self.canvas, grid_map)

            for key in self.new_data[0]:
                new_prop = self.new_data[0][key]
                new_group = groups[new_prop[2]]
                now_prop = new_prop
                now_group = new_group
                draw_rect(
                    self.canvas, (int(now_group[2]), int(now_group[3]), int(now_group[4])),
                    (
                        now_prop[0] * grid_size - view_position[0],
                        now_prop[1] * grid_size - view_position[1]
                    ),
                    now_group[0] * grid_size,
                    now_group[1] * grid_size
                )

            for key, event_x, event_y in self.new_data[1]:
                if key not in self.new_data[0]:
                    continue
                new_prop = self.new_data[0][key]
                new_group = groups[new_prop[2]]
                now_prop = new_prop
                now_group = new_group
                draw_line(
                    self.canvas, attack_line_rgb,
                    (
                        now_prop[0] * grid_size - view_position[0] + now_group[0] / 2 * grid_size,
                        now_prop[1] * grid_size - view_position[1] + now_group[1] / 2 * grid_size
                    ),
                    (
                        event_x * grid_size - view_position[0] + grid_size / 2,
                        event_y * grid_size - view_position[1] + grid_size / 2
                    )
                )
                draw_rect(
                    self.canvas, attack_dot_rgb,
                    (
                        event_x * grid_size - view_position[0] + grid_size / 2 - attack_dot_size * grid_size / 2,
                        event_y * grid_size - view_position[1] + grid_size / 2 - attack_dot_size * grid_size / 2,
                    ),
                    attack_dot_size * grid_size,
                    attack_dot_size * grid_size
                )

            if status or triggered or self.animation_progress < animation_total + animation_stop:
                self.animation_progress += 1

            self.display.blit(self.canvas, (0, 7))

            height_now = 0
            for texts in self.get_banners(self.frame_id, resolution):
                content = []
                width, height = 0, 0
                for text in texts:
                    text = banner_formatter.render(text[0], True, pygame.Color(*text[1]))
                    content.append((text, width))
                    width += text.get_width()
                    height = max(height, text.get_height())
                start = (resolution[0] - width) / 2.0
                for b in content:
                    self.display.blit(b[0], (start + b[1], height_now))
                height_now += height + banner_spacing

        if self.need_static_update:
            self.need_static_update = False

        observation = pygame.surfarray.pixels3d(self.display)
        new_observation = np.copy(observation)
        del observation
        if self.mode == 'human':
            pygame.display.flip()
        return np.transpose(new_observation, axes=(1, 0, 2)) if mode == "rgb_array" else None
