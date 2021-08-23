import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
import pygame

RENDER_RATIO = 2


class CakePaddle(pygame.sprite.Sprite):

    def __init__(self, speed=12):
        # surf is the right-most (largest) tier of the cake
        self.surf = pygame.Surface((30 // RENDER_RATIO, 120 // RENDER_RATIO))
        self.rect = self.surf.get_rect()
        self.surf2 = pygame.Surface((30 // RENDER_RATIO, 80 // RENDER_RATIO))
        self.rect2 = self.surf2.get_rect()
        self.surf3 = pygame.Surface((30 // RENDER_RATIO, 40 // RENDER_RATIO))
        self.rect3 = self.surf3.get_rect()
        self.surf4 = pygame.Surface((30 // RENDER_RATIO, 10 // RENDER_RATIO))
        self.rect4 = self.surf4.get_rect()

        self.speed = speed

    def reset(self):
        # self.rect is set from env class
        self.rect2.midright = self.rect.midleft
        self.rect3.midright = self.rect2.midleft
        self.rect4.midright = self.rect3.midleft

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 255, 255), self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect2)
        pygame.draw.rect(screen, (255, 255, 255), self.rect3)
        pygame.draw.rect(screen, (255, 255, 255), self.rect4)

    def update(self, area, action):
        # action: 1 - up, 2 - down
        movepos = [0, 0]
        if action == 1:
            movepos[1] = movepos[1] - self.speed
        elif action == 2:
            movepos[1] = movepos[1] + self.speed

        newpos = self.rect.move(movepos)
        if area.contains(newpos):
            self.rect = newpos
            # move other rects too
            self.rect2 = self.rect2.move(movepos)
            self.rect3 = self.rect3.move(movepos)
            self.rect4 = self.rect4.move(movepos)

    def process_collision(self, b_rect, dx, dy, b_speed, paddle_type):
        '''

        Parameters
        ----------
        b_rect : Ball rect
        dx, dy : Ball speed along single axis
        b_speed : Ball speed
        ignore paddle type

        Returns
        -------
        is_collision: 1 if ball collides with paddle
        b_rect: new ball rect
        b_speed: new ball speed

        '''
        if self.rect4.colliderect(b_rect):
            is_collision = True
            if dx > 0:
                b_rect.right = self.rect4.left
                b_speed[0] = -b_speed[0]
            # top or bottom edge
            elif dy > 0:
                b_rect.bottom = self.rect4.top
                b_speed[1] = -b_speed[1]
            elif dy < 0:
                b_rect.top = self.rect4.bottom
                b_speed[1] = -b_speed[1]
            return is_collision, b_rect, b_speed
        elif self.rect3.colliderect(b_rect):
            is_collision = True
            if dx > 0:
                b_rect.right = self.rect3.left
                b_speed[0] = -b_speed[0]
            # top or bottom edge
            elif dy > 0:
                b_rect.bottom = self.rect3.top
                b_speed[1] = -b_speed[1]
            elif dy < 0:
                b_rect.top = self.rect3.bottom
                b_speed[1] = -b_speed[1]
            return is_collision, b_rect, b_speed
        elif self.rect2.colliderect(b_rect):
            is_collision = True
            if dx > 0:
                b_rect.right = self.rect2.left
                b_speed[0] = -b_speed[0]
            # top or bottom edge
            elif dy > 0:
                b_rect.bottom = self.rect2.top
                b_speed[1] = -b_speed[1]
            elif dy < 0:
                b_rect.top = self.rect2.bottom
                b_speed[1] = -b_speed[1]
            return is_collision, b_rect, b_speed
        elif self.rect.colliderect(b_rect):
            is_collision = True
            if dx > 0:
                b_rect.right = self.rect.left
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
