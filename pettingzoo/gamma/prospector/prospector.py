import pygame
import pygame as pg
import os
import random
import gym
import numpy as np

# Define some colors

PLAYER_SPEED = 30.0
PLAYER_ROT_SPEED = 20.0
PLAYER_IMG = "manBlue_gun.png"
PLAYER_HIT_RECT = pg.Rect(0, 0, 35, 35)
TILESIZE = 2

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

_image_library = {}
vec = pygame.math.Vector2


def get_image(path):
    global _image_library
    image = _image_library.get(path)
    if image is None:
        canonicalized_path = path.replace("/", os.sep).replace("\\", os.sep)
        image = pygame.image.load(canonicalized_path)
        _image_library[path] = image
    return image


def get_small_random_value():
    # generates a small random value between [0, 1/100)
    return (1 / 100) * np.random.rand()


class Block(pygame.sprite.Sprite):
    """
    This class represents the ball.
    It derives from the "Sprite" class in Pygame.
    """

    def __init__(self, color=(250, 250, 0), width=20, height=20):
        """ Constructor. Pass in the color of the block,
        and its size. """

        # Call the parent class (Sprite) constructor
        super().__init__()

        # Create an image of the block, and fill it with a color.
        # This could also be an image loaded from the disk.
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        # Fetch the rectangle object that has the dimensions of the image
        # image.
        # Update the position of this object by setting the values
        # of rect.x and rect.y
        self.rect = self.image.get_rect()
        self.dim = self.rect.size

    def reset_pos(self):
        self.rect.y = random.randrange(0, 20)
        self.rect.x = random.randrange(0, self.screen_width[0])
        # print(self.rect.y, self.rect.x)

    def update(self, pos, corner):
        """
        rect corner numbers
        1-----2
        |     |
        4-----3
        """
        self.rect.bottomright = (pos.x, pos.y)


class agent1(pygame.sprite.Sprite):
    """
    This class represents the ball
    """

    def __init__(self, _screen_width, x, y, speed=20):
        """ Constructor. Pass in the color of the block,
        and its x and y position. """
        # Call the parent class (Sprite) constructor
        super().__init__()

        self.image = get_image("agent1.jpg")
        self.base_image = get_image("agent1.jpg")
        self.screen_width = _screen_width
        self.rect = self.image.get_rect()
        self.dim = self.rect.size

        self.speed_val = speed
        self.vel = vec(
            int(self.speed_val * np.cos(np.pi / 4)),
            int(self.speed_val * np.sin(np.pi / 4)),
        )
        self.rot = 0
        self.bounce_randomness = 1
        self.pos = vec(x, y) * TILESIZE
        self.collision = [False] * 9

    def handle_keyboard_input(self):
        self.rot_speed = 0
        self.vel = vec(0, 0)
        keys = pygame.key.get_pressed()
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            print("Left")
            self.rot_speed = PLAYER_ROT_SPEED
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.rot_speed = -PLAYER_ROT_SPEED
            print("Right")
        if keys[pg.K_UP] or keys[pg.K_w]:
            self.vel = vec(PLAYER_SPEED, 0).rotate(-self.rot)
            print("Up")
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.vel = vec(-PLAYER_SPEED / 2, 0).rotate(-self.rot)
            print("down")

    def reset_pos(self):
        self.rect.y = random.randrange(350, 600)
        self.rect.x = random.randrange(0, self.screen_width[0])
        print(self.rect.y, self.rect.x)

    def update(self, pos, area, p1):
        """ Called each frame. """
        self.handle_keyboard_input()
        self.rot = (self.rot + self.rot_speed) % 360
        self.image = pg.transform.rotate(self.base_image, self.rot)
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.base_image.get_rect()
        self.rect.center = self.pos
        self.pos += self.vel
        # print(':::::::::',self.rect.x,self.rect.y)
        if self.vel[0] != 0:
            done_x = self.move_single_axis(self.vel[0], 0, area, p1)
        if self.vel[1] != 0:
            done_y = self.move_single_axis(0, self.vel[1], area, p1)

    def check_collision(self, rect):
        self.collision[0] = rect.collidepoint(self.rect.topleft)
        self.collision[1] = rect.collidepoint(self.rect.topright)
        self.collision[2] = rect.collidepoint(self.rect.bottomleft)
        self.collision[3] = rect.collidepoint(self.rect.bottomright)

        self.collision[4] = rect.collidepoint(self.rect.midleft)
        self.collision[5] = rect.collidepoint(self.rect.midright)
        self.collision[6] = rect.collidepoint(self.rect.midtop)
        self.collision[7] = rect.collidepoint(self.rect.midbottom)
        self.collision[8] = rect.collidepoint(self.rect.center)

        if True in self.collision:
            return self.collision.index(True)
        else:

            print(self.rect.topleft, self.rect.midtop, self.rect.midleft)

            for x in range(self.rect.topleft[0], self.rect.midtop[0]):
                if rect.collidepoint(x, self.rect.topleft[1]):
                    self.collision[0] = True
            for y in range(self.rect.topleft[1], self.rect.midleft[1]):
                if rect.collidepoint(self.rect.topleft[0], y):
                    self.collision[0] = True

            for x in range(self.rect.bottomleft[1], self.rect.midbottom[1]):
                if rect.collidepoint(x, self.rect.bottomleft[0]):
                    self.collision[2] = True
            for y in range(self.rect.bottomleft[0], self.rect.midleft[0]):
                if rect.collidepoint(self.rect.bottomleft[1], y):
                    self.collision[2] = True
            print("collision:", self.collision)
            return self.collision.index(True)

    def rotate(self, angle):
        self.image = pygame.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def move_single_axis(self, dx, dy, area, p1):
        # returns done

        # move ball rect
        self.rect.x += dx
        self.rect.y += dy

        if not area.contains(self.rect):
            # bottom wall
            if dy > 0:
                self.rect.bottom = area.bottom
                self.vel[1] = -self.vel[1]
            # top wall
            elif dy < 0:
                self.rect.top = area.top
                self.vel[1] = -self.vel[1]
            # right or left walls
            else:
                self.vel[0] = -self.vel[0]
                return True

        else:
            # Do ball and bat collide?
            # add some randomness
            r_val = 0
            if self.bounce_randomness:
                r_val = get_small_random_value()

            # ball in left half of screen
            is_collision, self.rect, self.vel = p1.process_collision(
                self.rect, dx, dy, self.vel
            )
            if is_collision:
                self.vel = vec(
                    0, 0
                )  # self.speed[0] + np.sign(self.speed[0]) * r_val, self.speed[1] + np.sign(self.speed[1]) * r_val]

        return False

    def process_collision(self, b_rect, dx, dy, b_speed):
        if self.rect.colliderect(b_rect):
            is_collision = True
            if dx < 0:
                b_rect.left = self.rect.right
                b_speed[0] = -b_speed[0]
            # top or bottom edge
            elif dy > 0:
                b_rect.bottom = self.rect.top
                b_speed[1] = -b_speed[1]
            elif dy < 0:
                b_rect.top = self.rect.bottom
                b_speed[1] = -b_speed[1]
            return is_collision, b_rect, b_speed
        return False, b_rect, b_speed


class agent2(pygame.sprite.Sprite):
    """
    This class represents the triangle
    """

    def __init__(self, _screen_width, speed=5):
        """ Constructor. Pass in the color of the block,
        and its x and y position. """
        # Call the parent class (Sprite) constructor
        super().__init__()

        self.image = get_image(
            "agent2.jpg"
        )  # pygame.draw.polygon(screen, BLACK, [[0, 0], [0, 50], [50, 0]], 5)#
        self.screen_width = _screen_width
        self.rect = self.image.get_rect()
        self.dim = self.rect.size
        self.rect.y = 350
        self.mode = True

        self.speed_val = speed
        self.vel = vec(
            int(self.speed_val * np.cos(np.pi / 4)),
            int(self.speed_val * np.sin(np.pi / 4)),
        )
        self.hit = False
        self.bounce_randomness = 1

    def reset_pos(self):
        self.rect.y = random.randrange(350, 600)
        self.rect.x = random.randrange(0, self.screen_width[0])
        # print(self.rect.y, self.rect.x)

    def update(self, pos):
        """ Called each frame. """
        if self.mode:
            # if self.rect.x > 1000:
            #     self.rect.x = 0
            # self.rect.x += 5
            if self.rect.y > 100:
                self.rect.center = pos
                # self.rect.x = pos[0]
            # else:
            #     self.reset_pos()

        else:
            if self.rect.y < 100:
                self.change_command()
                self.rect.y = 350
            self.rect.y -= 5

    def change_command(self):
        self.mode = not self.mode

    def process_collision(self, b_rect, dx, dy, b_speed):
        if self.rect.colliderect(b_rect):
            is_collision = True
            if dx < 0:
                b_rect.left = self.rect.right
                b_speed[0] = -b_speed[0]
            # top or bottom edge
            elif dy > 0:
                b_rect.bottom = self.rect.top
                b_speed[1] = -b_speed[1]
            elif dy < 0:
                b_rect.top = self.rect.bottom
                b_speed[1] = -b_speed[1]
            return is_collision, b_rect, b_speed
        return False, b_rect, b_speed

    def move_single_axis(self, dx, dy, area, p1):
        self.rect.x += dx
        self.rect.y += dy

        if not area.contains(self.rect):
            # bottom wall
            if dy > 0:
                self.rect.bottom = area.bottom
                self.vel[1] = -self.vel[1]
            # top wall
            elif dy < 0:
                self.rect.top = area.top
                self.vel[1] = -self.vel[1]
            # right or left walls
            else:
                self.vel[0] = -self.vel[0]
                return True

        else:
            r_val = 0
            if self.bounce_randomness:
                r_val = get_small_random_value()

            # ball in left half of screen
            is_collision, self.rect, self.vel = p1.process_collision(
                self.rect, dx, dy, self.vel
            )
            if is_collision:
                self.vel = vec(
                    0, 0
                )  # self.speed[0] + np.sign(self.speed[0]) * r_val, self.speed[1] + np.sign(self.speed[1]) * r_val]

        return False


class env(gym.Env):
    def __init__(self):
        super(env, self).__init__()
        global agent2, agent1
        pygame.init()

        # Set the width and height of the screen [width, height]
        size = (1002, 699)
        self.screen = pygame.display.set_mode(size)
        background = get_image("background.jpg")
        pygame.display.set_caption("My Game")
        self.screen.blit(background, (0, 0))
        self.area = self.screen.get_rect()

        # Loop until the user clicks the close button.
        done = False

        # Used to manage how fast the screen updates
        clock = pygame.time.Clock()
        agent1 = agent1(size, x=50, y=50, speed=20)
        agent2 = agent2(size)

        block_list, all_sprites_list = self.create_targets()

        vis = pygame.sprite.Group()  # Visualize block that is being carried by agent 1
        vis2 = pygame.sprite.Group()  # Visualize block that is being carried by agent 2
        block_picked = None
        block_transfered = None
        flag = 0
        blocks_hit_list = []
        # cropped = pygame.Surface((100,100))

        # -------- Main Program Loop -----------
        while not done:
            # --- Main event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True

            self.screen.blit(background, (0, 0))
            self.screen.blit(agent1.image, agent1.rect)
            # cropped.blit(agent1.image, (agent1.rect.x,agent1.rect.y))
            self.screen.blit(agent2.image, agent2.rect)
            pos = pygame.mouse.get_pos()
            agent1.update(pos, self.area, agent2)
            agent2.update(pos)  # , self.area, agent1)
            if flag == 0:
                blocks_hit_list = pygame.sprite.spritecollide(agent1, block_list, True)
            pygame.draw.circle(self.screen, RED, agent1.rect.topleft, 5)
            while len(blocks_hit_list) > 1:
                block_list.add(blocks_hit_list.pop())
            if blocks_hit_list:
                # print(len(blocks_hit_list), len(block_list))
                vis.add(blocks_hit_list[0])
                block_picked = blocks_hit_list[0]
                flag = 1
            if block_picked:
                corner = agent1.check_collision(block_picked.rect)

                block_picked.update(agent1.rect, corner)
                agent1.rotate_flag = True
            # --- Go ahead and update the screen with what we've drawn.
            # print(len(block_list))
            if agent1.rect.y < 355:
                flag = 0
                block_picked = None
                # agent1.rotate_flag = False

            blocks_transfer_list = pygame.sprite.spritecollide(agent2, vis, True)
            if blocks_transfer_list:
                block_transfered = blocks_transfer_list[0]
                block_transfered.update(agent2.rect)
                vis2.add(block_transfered)
                agent2.change_command()
                block_picked = None
                flag = 0

            if block_transfered:
                block_transfered.update(agent2.rect)
            if agent2.rect.y < 105:
                block_transfered = None

            block_list.draw(self.screen)
            vis.draw(self.screen)
            vis2.draw(self.screen)
            pygame.display.flip()
            clock.tick(10)

        pygame.quit()

    def create_targets(self):
        block_list = pygame.sprite.Group()

        # This is a list of every sprite.
        # All blocks and the player block as well.
        all_sprites_list = pygame.sprite.Group()
        x = 20
        for i in range(18):
            # This represents a block
            block = Block()
            # Set a random location for the block
            block.rect.x = x
            x += 75
            block.rect.y = 630
            # Add the block to the list of objects
            block_list.add(block)
            all_sprites_list.add(block)

        return block_list, all_sprites_list
