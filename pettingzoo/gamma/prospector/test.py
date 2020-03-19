import pygame as pg
from pygame.locals import *
import pymunk as pm
from pymunk import Vec2d

import math
import os
from enum import IntEnum, auto
import itertools as it


SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT = (1280, 720)

WALL_WIDTH = 100

WATER_HEIGHT = 100

PLAYER_SPRITE_RADIUS = 16.5

def load_image(path: list) -> pg.Surface: # All images stored in data/
    img = pg.image.load(os.path.join('data', *path))
    img = img.convert_alpha()
    return img


def flipy(p):
    """Convert chipmunk coordinates to pygame coordinates."""
    return Vec2d(p[0], -p[1] + 600)

def invert_y(points):
    return [(x, -y) for x, y in points]

class CollisionTypes(IntEnum):
    PROSPECTOR = auto()
    BOUNDARY = auto()
    WATER = auto()
    CHEST = auto()
    GOLD = auto()
    BANKER = auto()


class Prospector(pg.sprite.Sprite):
    def __init__(self, pos, space, mass=1):
        super().__init__()
        self.image = load_image(['prospec.png'])

        self.rect = self.image.get_rect()
        self.orig_image = self.image

        # Create the physics body and shape of this object.
        # moment = pm.moment_for_poly(mass, vertices)

        moment = pm.moment_for_circle(mass, 0, self.rect.width / 2)

        self.body = pm.Body(mass, moment)
        self.body.nugget = None
        # self.shape = pm.Poly(self.body, vertices, radius=3)

        self.shape = pm.Circle(self.body, PLAYER_SPRITE_RADIUS)
        self.shape.elasticity = 0.0
        self.shape.collision_type = CollisionTypes.PROSPECTOR

        self.body.position = flipy(pos)
        # Add them to the Pymunk space.
        self.space = space
        self.space.add(self.body, self.shape)

        self.accel_forw = False
        self.accel_back = False
        self.turn_left = False
        self.turn_right = False
        self.topspeed = 500
        self.angle = 0

    # def handle_event(self, event):
    #     if event.type == pg.KEYDOWN:
    #         if event.key == pg.K_w:
    #             self.accel_forw = True
    #         if event.key == pg.K_a:
    #             self.turn_left = True
    #         if event.key == pg.K_d:
    #             self.turn_right = True
    #         if event.key == pg.K_s:
    #             self.accel_back = True
    #     if event.type == pg.KEYUP:
    #         if event.key == pg.K_w:
    #             self.accel_forw = False
    #         if event.key == pg.K_a:
    #             self.turn_left = False
    #         if event.key == pg.K_d:
    #             self.turn_right = False
    #         if event.key == pg.K_s:
    #             self.accel_back = False

    def update(self, delta, keys):
        # Accelerate the pymunk body of this sprite.
        # if self.accel_forw and self.body.velocity.length < self.topspeed:
        #     # self.body.apply_force_at_local_point(Vec2d(0, 624), Vec2d(0, 0))
        #     self.body.apply_impulse_at_local_point(Vec2d(0, 50))
        #     # self.body.velocity += (0, 15)
        # if self.accel_back and self.body.velocity.length < self.topspeed:
        #     # self.body.apply_force_at_local_point(Vec2d(0, -514), Vec2d(0, 0))
        #     self.body.apply_impulse_at_local_point(Vec2d(0, -50))
        # if self.turn_left and self.body.velocity.length < self.topspeed:
        #     self.body.angle += 0.1
        #     self.body.angular_velocity = 0
        # if self.turn_right and self.body.velocity.length < self.topspeed:
        #     self.body.angle -= 0.1
        #     self.body.angular_velocity = 0
        if keys[K_w] and self.body.velocity.length < self.topspeed:
            # self.body.apply_force_at_local_point(Vec2d(0, 624), Vec2d(0, 0))
            self.body.apply_impulse_at_local_point(Vec2d(0, 200))
            # self.body.velocity = Vec2d(0, 1).rotated(self.body.angle) * 300
            # self.body.velocity += (0, 15)
        if keys[K_s] and self.body.velocity.length < self.topspeed:
            # self.body.apply_force_at_local_point(Vec2d(0, -514), Vec2d(0, 0))
            self.body.apply_impulse_at_local_point(Vec2d(0, -50))
        if keys[K_d] and self.body.velocity.length < self.topspeed:
            # self.body.apply_force_at_local_point(Vec2d(0, -514), Vec2d(0, 0))
            self.body.apply_impulse_at_local_point(Vec2d(50, 0))
        if keys[K_a] and self.body.velocity.length < self.topspeed:
            # self.body.apply_force_at_local_point(Vec2d(0, -514), Vec2d(0, 0))
            self.body.apply_impulse_at_local_point(Vec2d(-50, 0))
        if keys[K_q] and self.body.velocity.length < self.topspeed:
            self.body.angle += 0.1
            self.body.angular_velocity = 0
        if keys[K_e] and self.body.velocity.length < self.topspeed:
            self.body.angle -= 0.1
            self.body.angular_velocity = 0
        # Rotate the image of the sprite.
        self.angle = self.body.angle
        # print(self.body.position)
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
    def __init__(self, pos, space, *sprite_groups):
        super().__init__(sprite_groups)
        self.image = load_image(['banker.png'])

        self.rect = self.image.get_rect()
        self.orig_image = self.image

        # Create the physics body and shape of this object.
        # moment = pm.moment_for_poly(mass, vertices)

        moment = pm.moment_for_circle(1, 0, self.rect.width / 2)

        self.body = pm.Body(1, moment)
        self.body.nugget = None
        self.body.nugget_offset = None
        # self.shape = pm.Poly(self.body, vertices, radius=3)

        self.shape = pm.Circle(self.body, PLAYER_SPRITE_RADIUS)
        self.shape.collision_type = CollisionTypes.BANKER

        self.body.position = flipy(pos)
        # Add them to the Pymunk space.
        self.space = space
        self.space.add(self.body, self.shape)

        self.accel_forw = False
        self.accel_back = False
        self.turn_left = False
        self.turn_right = False
        self.topspeed = 1790
        self.angle = 0

    # def handle_event(self, event):
    #     if event.type == pg.KEYDOWN:
    #         if event.key == pg.K_w:
    #             self.accel_forw = True
    #         if event.key == pg.K_a:
    #             self.turn_left = True
    #         if event.key == pg.K_d:
    #             self.turn_right = True
    #         if event.key == pg.K_s:
    #             self.accel_back = True
    #     if event.type == pg.KEYUP:
    #         if event.key == pg.K_w:
    #             self.accel_forw = False
    #         if event.key == pg.K_a:
    #             self.turn_left = False
    #         if event.key == pg.K_d:
    #             self.turn_right = False
    #         if event.key == pg.K_s:
    #             self.accel_back = False

    def update(self, delta, keys):
        # Accelerate the pymunk body of this sprite.
        # if self.accel_forw and self.body.velocity.length < self.topspeed:
        #     # self.body.apply_force_at_local_point(Vec2d(0, 624), Vec2d(0, 0))
        #     self.body.apply_impulse_at_local_point(Vec2d(0, 50))
        #     # self.body.velocity += (0, 15)
        # if self.accel_back and self.body.velocity.length < self.topspeed:
        #     # self.body.apply_force_at_local_point(Vec2d(0, -514), Vec2d(0, 0))
        #     self.body.apply_impulse_at_local_point(Vec2d(0, -50))
        # if self.turn_left and self.body.velocity.length < self.topspeed:
        #     self.body.angle += 0.1
        #     self.body.angular_velocity = 0
        # if self.turn_right and self.body.velocity.length < self.topspeed:
        #     self.body.angle -= 0.1
        #     self.body.angular_velocity = 0
        if keys[K_UP] and self.body.velocity.length < self.topspeed:
            # self.body.apply_force_at_local_point(Vec2d(0, 624), Vec2d(0, 0))
            self.body.apply_impulse_at_local_point(Vec2d(0, 50))
            # self.body.velocity += (0, 15)
        if keys[K_DOWN] and self.body.velocity.length < self.topspeed:
            # self.body.apply_force_at_local_point(Vec2d(0, -514), Vec2d(0, 0))
            self.body.apply_impulse_at_local_point(Vec2d(0, -50))
        if keys[K_RIGHT] and self.body.velocity.length < self.topspeed:
            # self.body.apply_force_at_local_point(Vec2d(0, -514), Vec2d(0, 0))
            self.body.apply_impulse_at_local_point(Vec2d(50, 0))
        if keys[K_LEFT] and self.body.velocity.length < self.topspeed:
            # self.body.apply_force_at_local_point(Vec2d(0, -514), Vec2d(0, 0))
            self.body.apply_impulse_at_local_point(Vec2d(-50, 0))
        # Rotate the image of the sprite.
        self.angle = self.body.angle
        self.rect.center = flipy(self.body.position)
        self.image = pg.transform.rotozoom(
            self.orig_image, math.degrees(self.body.angle), 1
        )

        self.rect = self.image.get_rect(center=self.rect.center)

        curr_vel = self.body.velocity

        if self.body.nugget != None:
            self.body.nugget.update(self.body.position, self.body.nugget_offset, True)

        self.body.velocity = curr_vel


# Not necessary to show on the screen, so we won't use pygame to initialize
class Boundary(pg.sprite.Sprite):
    def __init__(self, w_type, pos, verts, space, *sprite_groups):
        super().__init__(sprite_groups)

        if w_type == 'top':
            self.image = load_image(['horiz-wall.png'])
            self.rect = self.image.get_rect(topleft=(0, pos[1]))
        elif w_type == 'right':
            self.image = load_image(['vert-wall.png'])
            self.rect = self.image.get_rect(topleft=(pos[0], 0))
        elif w_type == 'left':
            self.image = load_image(['vert-wall.png'])
            self.rect = self.image.get_rect(topleft=(pos[0], 0))

        self.body = pm.Body(body_type=pm.Body.STATIC)
        # Need to transform the vertices for the pymunk poly shape,
        # so that they fit to the image vertices.
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
        # Need to transform the vertices for the pymunk poly shape,
        # so that they fit to the image vertices.
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

        self.image = load_image(['chest.png'])
        self.rect = self.image.get_rect(topleft=pos)

        self.body = pm.Body(body_type=pm.Body.STATIC)
        self.body.score = 0
        # Need to transform the vertices for the pymunk poly shape,
        # so that they fit to the image vertices.
        invert_verts = invert_y(verts)
        self.shape = pm.Poly(self.body, invert_verts)
        self.shape.collision_type = CollisionTypes.CHEST

        self.body.position = flipy(pos)
        self.space = space
        self.space.add(self.shape, self.body)

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

        # self.start_vec = pos - body.position
        # print('Initial:', self.start_vec)

        # print('Prospector angle:', body.angle)

        self.initial_angle = body.angle - Vec2d(0, -1).angle
        self.parent_body = body
        # print('Initial: ', self.initial_angle)

    def update(self, pos, angle, banker: bool):
        # Accelerate the pymunk body of this sprite.
        # Rotate the image of the sprite.

        if banker:
            new_angle = angle
        else:
            new_angle = angle - self.initial_angle
        new_pos = pos + Vec2d(PLAYER_SPRITE_RADIUS + 9, 0).rotated(new_angle)

        # print(parent_body.angle + self.base_pos.angle)
        # print(new_pos)

        self.body.position = new_pos
        # self.body.angle = parent_body.angle
        self.body.angular_velocity = 0
        # self.angle = self.body.angle
        # # print(self.body.position)
        self.rect.center = flipy(self.body.position)
        self.image = pg.transform.rotozoom(
            self.orig_image, math.degrees(self.body.angle), 1
        )
        self.rect = self.image.get_rect(center=self.rect.center)

        # print('Gold:', self.body.angular_velocity, self.body.velocity)

    def draw(self, surf):
        surf.blit(self.image, self.rect)


class Game:
    def __init__(self):
        self.done = False
        self.screen = pg.display.set_mode(SCREEN_SIZE)
        self.clock = pg.time.Clock()
        self.bg_color = pg.Color(100, 100, 100)

        self.space = pm.Space()
        self.space.gravity = Vec2d(0.0, 0.0)
        # self.space.damping = 0.5
        self.space.damping = 0.0

        self.all_sprites = pg.sprite.Group()
        self.gold = []

        self.player = Prospector((1000, 500), self.space)
        self.all_sprites.add(self.player)
        # Position-vertices tuples for the walls.
        # vertices = [
        #     ([80, 120], ((0, 0), (100, 0), (70, 100), (0, 100))),
        #     ([400, 250], ((20, 40), (100, 0), (80, 80), (10, 100))),
        #     ([200, 450], ((20, 40), (300, 0), (300, 120), (10, 100))),
        #     ([760, 10], ((0, 0), (30, 0), (30, 420), (0, 400))),
        # ]

        banker_pos = (
            ((184 * 1) + 34, 250), ((184 * 3) + 34, 250), ((184 * 5) + 34, 250)
        )
        self.bankers = []
        for pos in banker_pos:
            self.bankers.append(Banker(pos, self.space, self.all_sprites))


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
            ('left',   [-WALL_WIDTH // 2, -WALL_WIDTH // 2], vertical_vertices),  # left boundary
            ('top',    [-WALL_WIDTH // 2, -WALL_WIDTH // 2], horiz_vertices),  # top boundary
            ('right',  [SCREEN_WIDTH - WALL_WIDTH // 2, -WALL_WIDTH // 2], vertical_vertices),  # right boundary
            # ('bottom', [-WALL_WIDTH // 2, SCREEN_HEIGHT], horiz_vertices), # bottom boundary
        ]

        # boundaries = [
        #     ('vert',   [-WALL_WIDTH // 2, -WALL_WIDTH // 2], vertical_vertices),  # left boundary
        #     ('horiz',    [-WALL_WIDTH // 2, -WALL_WIDTH // 2], horiz_vertices),  # top boundary
        #     ('vert',  [SCREEN_WIDTH, -WALL_WIDTH // 2], vertical_vertices),  # right boundary
        #     ('horiz', [-WALL_WIDTH // 2, SCREEN_HEIGHT], horiz_vertices), # bottom boundary
        # ]

        chest_verts = (
            (0, 0),
            (184, 0),
            (184, 100),
            (0, 100),
        )

        chests = [
            ([184 * 1, 50], chest_verts),
            ([184 * 3, 50], chest_verts),
            ([184 * 5, 50], chest_verts),
        ]

        for pos, verts in chests:
            Chest(pos, verts, self.space, self.all_sprites)

        water_info = {
            'pos' : (0, SCREEN_HEIGHT - WATER_HEIGHT), 
            'verts': ((0, 0), (SCREEN_WIDTH, 0), (SCREEN_WIDTH, WATER_HEIGHT), (0, WATER_HEIGHT))
        }

        Water(water_info['pos'], water_info['verts'], self.space, self.all_sprites)


        for w_type, pos, verts in boundaries:
            if w_type != 'bottom':
                Boundary(w_type, pos, verts, self.space, self.all_sprites)
            else:
                Boundary(w_type, pos, verts, self.space)

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

            print('hit')

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

            # prospec = gold.body.prospec
            gold_class.parent_body.nugget = None

            # self.player.body.nugget = None
            # prospec.nugget = None

            print(self.player.body.nugget)

            normal = arbiter.contact_point_set.normal

            gold_class.parent_body = banker.body
            banker.body.nugget = gold_class
            banker.body.nugget_offset = normal.angle

            print('BANKER hit')
            return False

        handoff_gold = self.space.add_collision_handler(
            CollisionTypes.BANKER,
            CollisionTypes.GOLD)

        handoff_gold.begin = handoff_gold_handler

        def wall_collision(arbiter, space, data):
            # print('Wall hit')
            prospec = arbiter.shapes[0]
            prospec_body = prospec.body

            position = arbiter.contact_point_set.points[0].point_a

            normal = arbiter.contact_point_set.normal

            prospec_body.position = position - (30 * normal)
            prospec_body.velocity = (0, 0)

            print(arbiter.contact_point_set.normal)

            print(position, prospec_body.position)

            return False

        prospector_hits_wall = self.space.add_collision_handler(
            CollisionTypes.PROSPECTOR,
            CollisionTypes.BOUNDARY)

        prospector_hits_wall.begin = wall_collision

        def gold_score_handler(arbiter, space, data):
            # print('Wall hit')
            gold, chest = arbiter.shapes[0], arbiter.shapes[1]

            chest.body.score += 1

            print(chest.body.score)

            self.space.remove(gold, gold.body)

            gold_class = None
            for g in self.gold:
                if g.id == gold.id:
                    gold_class = g

            gold_class.parent_body.nugget = None


            self.gold.remove(gold_class)
            self.all_sprites.remove(gold_class)

            return False

        gold_score = self.space.add_collision_handler(
            CollisionTypes.GOLD,
            CollisionTypes.CHEST)

        gold_score.begin = gold_score_handler


        self.player.filter = pm.ShapeFilter(
            categories=0b1, mask=pm.ShapeFilter.ALL_MASKS ^ 0b1
        )


    def run(self):
        while not self.done:
            for event in pg.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key in [K_ESCAPE]):
                    self.done = True

            self.dt = self.clock.tick(30) / 1000
            # print(self.player.body.nugget)
            # print(self.player.body.position, self.player.body.nugget)
            # if self.player.body.nugget != None:
            #     print('Nugget location:', self.player.body.nugget.body.position)
            self.run_logic()
            self.draw()

    # def handle_events(self):
    #     for event in pg.event.get():
    #         if event.type == pg.QUIT:
    #             self.done = True

    #         self.player.handle_event(event)

    def run_logic(self):
        self.space.step(1 / 60)
        self.all_sprites.update(self.dt, pg.key.get_pressed())

    def draw(self):
        self.screen.fill(self.bg_color)
        self.all_sprites.draw(self.screen)

        if self.player.body.nugget is not None:
            print('going')
            self.player.body.nugget.draw(self.screen)

        for b in self.bankers:
            if b.body.nugget is not None:
                print('draw')
                b.body.nugget.draw(self.screen)

        # Debug draw - Pymunk shapes are green, pygame rects are blue.
        for obj in self.all_sprites:
            # print(type(obj))
            shape = obj.shape
            if type(obj) not in [Prospector, Gold, Banker]:
                ps = [
                    flipy(pos.rotated(shape.body.angle) + shape.body.position)
                    for pos in shape.get_vertices()
                ]
                ps.append(ps[0])
                # pg.draw.rect(self.screen, pg.Color("blue"), obj.rect, 2)
                # pg.draw.lines(self.screen, (90, 200, 50), False, ps, 2)
            elif type(obj) == Prospector:
                # pg.draw.rect(self.screen, pg.Color("blue"), obj.rect, 2)
                pos = list(map(int, obj.body.position))
                pos = flipy(pos)
                # pg.draw.arc(self.screen, (90, 200, 50), obj.rect, 0, 6.28, 5)
            elif type(obj) == Gold:
                pg.draw.rect(self.screen, pg.Color("blue"), obj.rect, 2)
                # pos = list(map(int, obj.body.position))
                pos = flipy(pos)
                # pg.draw.arc(self.screen, (90, 200, 50), obj.rect, 0, 6.28, 5)


        pg.display.flip()


if __name__ == "__main__":
    pg.init()
    game = Game()
    game.run()
