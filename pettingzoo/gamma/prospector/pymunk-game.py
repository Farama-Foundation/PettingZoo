import pygame as pg
from pygame.locals import *
import pymunk as pm
from pymunk import Vec2d

import math
import os
from enum import IntEnum, auto
import itertools as it
from random import randint


SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT = (1280, 720)
BACKGROUND_COLOR = (217, 151, 106)

WALL_WIDTH = 100

WATER_HEIGHT = 100

PLAYER_SPRITE_RADIUS = 16.5

PLAYER_SPEED = 150
BANKER_SPEED = 100
BANKER_HANDOFF_TOLERANCE = math.pi / 4
TWO_PI = math.pi * 2.0

def load_image(path: list) -> pg.Surface: # All images stored in data/
    img = pg.image.load(os.path.join('data', *path))
    img = img.convert_alpha()
    return img


# Convert chipmunk coords to pymunk coords, flipping and offsetting y-coordinate
def flipy(point):
    return Vec2d(point[0], -point[1] + 600)

def invert_y(points):
    return [(x, -y) for x, y in points]

def rand_pos(sprite):
    x = randint(50, SCREEN_WIDTH - 50)
    if sprite == 'banker':
        return x, randint(150, 300)
    elif sprite == 'prospector':
        return x, randint(350, SCREEN_HEIGHT - (WATER_HEIGHT + 30))


def normalize_angle(angle):
    if angle > (math.pi):
        return angle - TWO_PI
    elif angle < 0.:
        return angle + TWO_PI
    return angle


class CollisionTypes(IntEnum):
    PROSPECTOR = auto()
    BOUNDARY = auto()
    WATER = auto()
    CHEST = auto()
    GOLD = auto()
    BANKER = auto()


class Prospector(pg.sprite.Sprite):
    def __init__(self, pos, space, *sprite_groups):
        super().__init__(sprite_groups)
        # self.image = load_image(['prospec.png'])
        self.image = load_image(['prospector-pickaxe.png'])
        self.image = pg.transform.scale(
            self.image, 
            (int(PLAYER_SPRITE_RADIUS * 2), int(PLAYER_SPRITE_RADIUS * 2))
        )

        self.rect = self.image.get_rect()
        self.orig_image = self.image

        # Create the physics body and shape of this object.
        # moment = pm.moment_for_poly(mass, vertices)

        moment = pm.moment_for_circle(1, 0, self.rect.width / 2)

        self.body = pm.Body(1, moment)
        self.body.nugget = None
        self.body.sprite_type = 'prospector'
        # self.shape = pm.Poly(self.body, vertices, radius=3)

        self.shape = pm.Circle(self.body, PLAYER_SPRITE_RADIUS)
        self.shape.elasticity = 0.0
        self.shape.collision_type = CollisionTypes.PROSPECTOR

        self.body.position = flipy(pos)
        # Add them to the Pymunk space.
        self.space = space
        self.space.add(self.body, self.shape)

    def update(self, delta, keys):
        x = y = 0
        if keys[K_w]:
            # self.body.apply_force_at_local_point(Vec2d(0, 624), Vec2d(0, 0))
            # self.body.apply_impulse_at_local_point(Vec2d(0, 200))
            # self.body.velocity = Vec2d(0, 1).rotated(self.body.angle) * PLAYER_SPEED
            y = 1
            # self.body.velocity += (0, 15)
        if keys[K_s]:
            # self.body.apply_force_at_local_point(Vec2d(0, -514), Vec2d(0, 0))
            # self.body.velocity = Vec2d(0, -1).rotated(self.body.angle) * PLAYER_SPEED
            y = -1
            # self.body.apply_impulse_at_local_point(Vec2d(0, -50))
        if keys[K_d]:
            # self.body.apply_force_at_local_point(Vec2d(0, -514), Vec2d(0, 0))
            # self.body.apply_impulse_at_local_point(Vec2d(50, 0))
            # self.body.velocity = Vec2d(1, 0).rotated(self.body.angle) * PLAYER_SPEED
            x = 1
        if keys[K_a]:
            # self.body.apply_force_at_local_point(Vec2d(0, -514), Vec2d(0, 0))
            # self.body.apply_impulse_at_local_point(Vec2d(-50, 0))
            # self.body.velocity = Vec2d(-1, 0).rotated(self.body.angle) * PLAYER_SPEED
            x = -1
        if keys[K_q]:
            self.body.angle += 0.1
            self.body.angular_velocity = 0
        if keys[K_e]:
            self.body.angle -= 0.1
            self.body.angular_velocity = 0

        if x != 0 and y != 0:
            self.body.velocity = (Vec2d(x, y).rotated(self.body.angle) * 
                                             (PLAYER_SPEED / math.sqrt(2)))
        else:
            self.body.velocity = Vec2d(x, y).rotated(self.body.angle) * PLAYER_SPEED

        # Rotate the image of the sprite.
        self.rect.center = flipy(self.body.position)
        self.image = pg.transform.rotozoom(
            self.orig_image, math.degrees(self.body.angle), 1
        )
        self.rect = self.image.get_rect(center=self.rect.center)

        curr_vel = self.body.velocity

        if self.body.nugget != None:
            self.body.nugget.update(self.body.position, self.body.angle, False)

        self.body.velocity = curr_vel


class Banker(pg.sprite.Sprite):
    def __init__(self, pos, space, num, *sprite_groups):
        super().__init__(sprite_groups)
        self.image = load_image(['bankers', '%s.png' % num])

        self.rect = self.image.get_rect()
        self.orig_image = self.image

        # Create the physics body and shape of this object.
        # moment = pm.moment_for_poly(mass, vertices)

        moment = pm.moment_for_circle(1, 0, self.rect.width / 2)

        self.body = pm.Body(1, moment)
        self.body.nugget = None
        self.body.sprite_type = 'banker'
        self.body.nugget_offset = None
        # self.shape = pm.Poly(self.body, vertices, radius=3)

        self.shape = pm.Circle(self.body, PLAYER_SPRITE_RADIUS)
        self.shape.collision_type = CollisionTypes.BANKER

        self.body.position = flipy(pos)
        # Add them to the Pymunk space.
        self.space = space
        self.space.add(self.body, self.shape)

    def update(self, delta, keys):
        # print(self.body.angle)
        # self.body.angle = math.pi / 2
        y = 0
        move = 0
        if any(keys[key] for key in (K_UP, K_DOWN, K_RIGHT, K_LEFT)):
            move = 1

        if keys[K_UP]:
            # self.body.apply_force_at_local_point(Vec2d(0, 624), Vec2d(0, 0))
            # self.body.apply_impulse_at_local_point(Vec2d(0, 50))
            # self.body.velocity += (0, 15)
            # self.body.velocity = Vec2d(0, 1).rotated(self.body.angle) * BANKER_SPEED
            self.body.angle = 0
        elif keys[K_DOWN]:
            # self.body.apply_force_at_local_point(Vec2d(0, -514), Vec2d(0, 0))
            # self.body.apply_impulse_at_local_point(Vec2d(0, -50))
            # self.body.velocity = Vec2d(0, -1).rotated(self.body.angle) * BANKER_SPEED
            self.body.angle = math.pi
        elif keys[K_RIGHT]:
            # self.body.apply_impulse_at_local_point(Vec2d(50, 0))
            # self.body.velocity = Vec2d(1, 0).rotated(self.body.angle) * BANKER_SPEED
            self.body.angle = -math.pi / 2
        elif keys[K_LEFT]:
            # self.body.apply_impulse_at_local_point(Vec2d(-50, 0))
            # self.body.velocity = Vec2d(-1, 0).rotated(self.body.angle) * BANKER_SPEED
            # self.body.angle = math.pi / 2
            self.body.angle = math.pi / 2

        self.body.velocity = Vec2d(0, move).rotated(self.body.angle) * BANKER_SPEED
        
        # else:
        #     self.body.velocity = Vec2d(x, y).rotated(self.body.angle) * BANKER_SPEED

        # Rotate the image of the sprite.
        self.rect.center = flipy(self.body.position)
        self.image = pg.transform.rotozoom(
            self.orig_image, math.degrees(self.body.angle), 1
        )

        self.rect = self.image.get_rect(center=self.rect.center)

        curr_vel = self.body.velocity

        if self.body.nugget != None:
            # self.body.nugget.update(self.body.position, self.body.nugget_offset, True)
            corrected = normalize_angle(self.body.angle + (math.pi / 2))
            self.body.nugget.update(self.body.position, corrected, True)

        self.body.velocity = curr_vel


class Boundary(pg.sprite.Sprite):
    def __init__(self, w_type, pos, verts, space, *sprite_groups):
        super().__init__(sprite_groups)

        # if w_type == 'top':
        #     self.image = load_image(['horiz-wall.png'])
        #     self.rect = self.image.get_rect(topleft=(0, pos[1] - WALL_WIDTH // 2))
        # elif w_type == 'right':
        #     self.image = load_image(['vert-wall.png'])
        #     self.rect = self.image.get_rect(topleft=(pos[0] + WALL_WIDTH // 2, 0))
        # elif w_type == 'left':
        #     self.image = load_image(['vert-wall.png'])
        #     self.rect = self.image.get_rect(topleft=(pos[0] - WALL_WIDTH // 2, 0))

        if w_type == 'top':
            self.image = load_image(['horiz-fence.png'])
            self.rect = self.image.get_rect(topleft=(0, pos[1] - WALL_WIDTH // 2))
        elif w_type == 'right':
            self.image = load_image(['vert-fence.png'])
            self.rect = self.image.get_rect(topleft=(pos[0] + WALL_WIDTH // 2, 0))
        elif w_type == 'left':
            self.image = load_image(['vert-fence.png'])
            self.rect = self.image.get_rect(topleft=(pos[0] - WALL_WIDTH // 2, 0))

        self.body = pm.Body(body_type=pm.Body.STATIC)

        # Transform pygame vertices to fit Pymunk body
        invert_verts = invert_y(verts)
        self.shape = pm.Poly(self.body, invert_verts)
        self.shape.elasticity = 0.0
        self.shape.collision_type = CollisionTypes.BOUNDARY

        self.body.position = flipy(pos)
        space.add(self.shape)


class Water(pg.sprite.Sprite):
    def __init__(self, pos, verts, space, *sprite_groups):
        super().__init__(*sprite_groups)
        # Determine the width and height of the surface.
        self.image = load_image(['water.png'])
        self.image = pg.transform.scale(self.image, (SCREEN_WIDTH, WATER_HEIGHT))

        self.rect = self.image.get_rect(topleft=pos)

        self.body = pm.Body(body_type=pm.Body.STATIC)

        # Transform pygame vertices to fit Pymunk body
        invert_verts = invert_y(verts)
        self.shape = pm.Poly(self.body, invert_verts)
        self.shape.collision_type = CollisionTypes.WATER

        # self.shape.friction = 1.0
        self.body.position = flipy(pos)
        self.space = space
        self.space.add(self.shape)

class Chest(pg.sprite.Sprite):
    def __init__(self, pos, verts, space, *sprite_groups):
        super().__init__(sprite_groups)

        self.image = load_image(['bank.png'])
        self.rect = self.image.get_rect(topleft=pos)

        self.body = pm.Body(body_type=pm.Body.STATIC)
        self.body.score = 0

        # Transform pygame vertices to fit Pymunk body
        invert_verts = invert_y(verts)
        self.shape = pm.Poly(self.body, invert_verts)
        self.shape.collision_type = CollisionTypes.CHEST

        self.body.position = flipy(pos)
        self.space = space
        self.space.add(self.shape, self.body)

    def __str__(self):
        return str(self.body.score)

class Gold(pg.sprite.Sprite):
    ids = it.count(0)

    def __init__(self, pos, body, space, *sprite_groups):
        super().__init__(sprite_groups)
        self.id = next(self.ids)

        self.image = load_image(['gold', '6.png'])
        self.image = pg.transform.scale(self.image, (16, 16))
        self.orig_image = self.image

        self.rect = self.image.get_rect()

        self.moment = pm.moment_for_circle(1, 0, 8)
        self.body = pm.Body(1, self.moment)
        self.body.position = body.position

        self.shape = pm.Circle(self.body, 8)
        self.shape.collision_type = CollisionTypes.GOLD
        self.shape.id = self.id

        self.space = space
        self.space.add(self.body, self.shape)

        self.initial_angle = body.angle - Vec2d(0, -1).angle
        self.parent_body = body

    def update(self, pos, angle, banker: bool):
        # Accelerate the pymunk body of this sprite.
        # Rotate the image of the sprite.

        if banker:
            new_angle = angle
        else:
            new_angle = angle - self.initial_angle
        new_pos = pos + Vec2d(PLAYER_SPRITE_RADIUS + 9, 0).rotated(new_angle)

        self.body.position = new_pos
        self.body.angular_velocity = 0
        self.rect.center = flipy(self.body.position)
        self.image = pg.transform.rotozoom(
            self.orig_image, math.degrees(self.body.angle), 1
        )
        self.rect = self.image.get_rect(center=self.rect.center)

    def draw(self, surf):
        surf.blit(self.image, self.rect)


class Game:
    def __init__(self):
        self.done = False
        self.screen = pg.display.set_mode(SCREEN_SIZE)
        self.clock = pg.time.Clock()

        self.space = pm.Space()
        self.space.gravity = Vec2d(0.0, 0.0)
        # self.space.damping = 0.5
        self.space.damping = 0.0

        self.all_sprites = pg.sprite.Group()
        self.gold = []

        prospec_info = [rand_pos('prospector') for _ in range(3)]
        self.prospectors = []
        for pos in prospec_info:
            self.prospectors.append(Prospector(pos, self.space, self.all_sprites))

        # self.player = Prospector((1000, 500), self.space)
        # self.all_sprites.add(self.player)
        # Position-vertices tuples for the walls.
        # vertices = [
        #     ([80, 120], ((0, 0), (100, 0), (70, 100), (0, 100))),
        #     ([400, 250], ((20, 40), (100, 0), (80, 80), (10, 100))),
        #     ([200, 450], ((20, 40), (300, 0), (300, 120), (10, 100))),
        #     ([760, 10], ((0, 0), (30, 0), (30, 420), (0, 400))),
        # ]

        # banker_pos = (
        #     (1, ((184 * 1) + 34, 250)), (2, ((184 * 3) + 34, 250)), (3, ((184 * 5) + 34, 250))
        # )
        banker_info = (
            (1, rand_pos('banker')), (2, rand_pos('banker')), (3, rand_pos('banker'))
        )
        self.bankers = []
        for num, pos in banker_info:
            self.bankers.append(Banker(pos, self.space, num, self.all_sprites))

        vertical_vertices = (
            (0, 0),
            (WALL_WIDTH, 0),
            (WALL_WIDTH, SCREEN_HEIGHT + (2 * WALL_WIDTH)),
            (0, SCREEN_HEIGHT + (2 * WALL_WIDTH)),
        )

        horiz_vertices = (
            (0, 0),
            (SCREEN_WIDTH + (2 * WALL_WIDTH), 0),
            (SCREEN_WIDTH + (2 * WALL_WIDTH), WALL_WIDTH),
            (0, WALL_WIDTH),
        )

        boundaries = [
            ('left',   [0, 0], vertical_vertices),  # left boundary
            ('top',    [0, 0], horiz_vertices),  # top boundary
            ('right',  [SCREEN_WIDTH - WALL_WIDTH, 0], vertical_vertices),  # 
            # ('left',   [-WALL_WIDTH // 2, -WALL_WIDTH // 2], vertical_vertices),  # left boundary
            # ('top',    [-WALL_WIDTH // 2, -WALL_WIDTH // 2], horiz_vertices),  # top boundary
            # ('right',  [SCREEN_WIDTH - WALL_WIDTH // 2, -WALL_WIDTH // 2], vertical_vertices),  # right boundary
            # ('bottom', [-WALL_WIDTH // 2, SCREEN_HEIGHT], horiz_vertices), # bottom boundary
        ]

        chest_verts = (
            (0, 0),
            (184, 0),
            (184, 85),
            (0, 85),
        )

        chest_info = [
            ([184 * 1, 50], chest_verts),
            ([184 * 3, 50], chest_verts),
            ([184 * 5, 50], chest_verts),
        ]

        self.chests = []
        for pos, verts in chest_info:
            self.chests.append(Chest(pos, verts, self.space, self.all_sprites))


        for w_type, pos, verts in boundaries:
            if w_type != 'bottom':
                Boundary(w_type, pos, verts, self.space, self.all_sprites)
            else:
                Boundary(w_type, pos, verts, self.space)

        water_info = {
            'pos' : (0, SCREEN_HEIGHT - WATER_HEIGHT), 
            'verts': ((0, 0), (SCREEN_WIDTH, 0), (SCREEN_WIDTH, WATER_HEIGHT), (0, WATER_HEIGHT))
        }

        Water(water_info['pos'], water_info['verts'], self.space, self.all_sprites)

        # for pos, verts in vertices:
        #     Wall(pos, verts, self.space, 1, self.all_sprites)

        def add_gold(arbiter, space, data):
            prospec = arbiter.shapes[0]
            prospec_body = prospec.body

            position = arbiter.contact_point_set.points[0].point_a
            normal = arbiter.contact_point_set.normal

            prospec_body.position = position - (24 * normal)
            prospec_body.velocity = (0, 0)

            if prospec_body.nugget == None:

                position = arbiter.contact_point_set.points[0].point_a

                gold = Gold(position, prospec_body, self.space)
                self.gold.append(gold)

                prospec_body.nugget = gold

            return True

        gold_dispenser = self.space.add_collision_handler(
            CollisionTypes.PROSPECTOR,
            CollisionTypes.WATER)

        gold_dispenser.begin = add_gold

        def handoff_gold_handler(arbiter, space, data):
            banker, gold = arbiter.shapes[0], arbiter.shapes[1]

            gold_class = None
            for g in self.gold:
                if g.id == gold.id:
                    gold_class = g

            if gold_class.parent_body.sprite_type == 'prospector':

                banker_body = banker.body

                normal = arbiter.contact_point_set.normal
                
                corrected = normalize_angle(banker_body.angle + (math.pi / 2))

                # print('Banker body angle:', banker_body.angle)
                # print('Corrected:', corrected)

                # if (banker_body.angle - BANKER_HANDOFF_TOLERANCE <= normal.angle <=
                #     banker_body.angle + BANKER_HANDOFF_TOLERANCE):
                if (corrected - BANKER_HANDOFF_TOLERANCE <= normal.angle <=
                    corrected + BANKER_HANDOFF_TOLERANCE):
                    # print(True)

                    # prospec = gold.body.prospec
                    gold_class.parent_body.nugget = None

                    # print(normal.angle)

                    gold_class.parent_body = banker_body
                    banker_body.nugget = gold_class
                    banker_body.nugget_offset = normal.angle

            return True

        handoff_gold = self.space.add_collision_handler(
            CollisionTypes.BANKER,
            CollisionTypes.GOLD)

        handoff_gold.begin = handoff_gold_handler

        def gold_score_handler(arbiter, space, data):
            gold, chest = arbiter.shapes[0], arbiter.shapes[1]

            gold_class = None
            for g in self.gold:
                if g.id == gold.id:
                    gold_class = g

            if gold_class.parent_body.sprite_type == 'banker':

                chest.body.score += 1

                self.space.remove(gold, gold.body)

                gold_class.parent_body.nugget = None

                total_score = ', '.join(['Chest %d: %d' % (i, c.body.score) 
                                        for i, c in enumerate(self.chests)])

                # print(total_score)

                self.gold.remove(gold_class)
                self.all_sprites.remove(gold_class)

            return False

        gold_score = self.space.add_collision_handler(
            CollisionTypes.GOLD,
            CollisionTypes.CHEST)

        gold_score.begin = gold_score_handler


        # self.player.filter = pm.ShapeFilter(
        #     categories=0b1, mask=pm.ShapeFilter.ALL_MASKS ^ 0b1
        # )


    def run(self):
        while not self.done:
            for event in pg.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key in [K_ESCAPE]):
                    self.done = True

            self.dt = self.clock.tick(15)

            self.space.step(1 / 15)
            self.all_sprites.update(self.dt, pg.key.get_pressed())

            self.draw()

    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)
        self.all_sprites.draw(self.screen)

        for p in self.prospectors:
            if p.body.nugget is not None:
                p.body.nugget.draw(self.screen)

        # if self.player.body.nugget is not None:
        #     self.player.body.nugget.draw(self.screen)

        for b in self.bankers:
            if b.body.nugget is not None:
                b.body.nugget.draw(self.screen)

        # Debug
        # for obj in self.all_sprites:
        #     # print(type(obj))
        #     shape = obj.shape
        #     if type(obj) not in [Prospector, Gold, Banker]:
        #         ps = [
        #             flipy(pos.rotated(shape.body.angle) + shape.body.position)
        #             for pos in shape.get_vertices()
        #         ]
        #         ps.append(ps[0])
        #         # pg.draw.rect(self.screen, pg.Color("blue"), obj.rect, 2)
        #         # pg.draw.lines(self.screen, (90, 200, 50), False, ps, 2)
        #     elif type(obj) == Prospector:
        #         # pg.draw.rect(self.screen, pg.Color("blue"), obj.rect, 2)
        #         pos = list(map(int, obj.body.position))
        #         pos = flipy(pos)
        #         # pg.draw.arc(self.screen, (90, 200, 50), obj.rect, 0, 6.28, 5)
        #     elif type(obj) == Gold:
        #         pg.draw.rect(self.screen, pg.Color("blue"), obj.rect, 2)
        #         # pos = list(map(int, obj.body.position))
        #         pos = flipy(pos)
        #         # pg.draw.arc(self.screen, (90, 200, 50), obj.rect, 0, 6.28, 5)


        pg.display.flip()


if __name__ == "__main__":
    pg.init()
    game = Game()
    game.run()
