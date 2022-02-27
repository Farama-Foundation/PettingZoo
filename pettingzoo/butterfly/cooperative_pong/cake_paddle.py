import os

import pygame


class CakePaddle(pygame.sprite.Sprite):

    def __init__(self, speed=12, render_ratio=2):
        self.render_ratio = render_ratio
        # surf is the right-most (largest) tier of the cake
        self.surf = pygame.Surface((30 // render_ratio, 120 // render_ratio))
        self.rect = self.surf.get_rect()
        self.surf2 = pygame.Surface((30 // render_ratio, 80 // render_ratio))
        self.rect2 = self.surf2.get_rect()
        self.surf3 = pygame.Surface((30 // render_ratio, 40 // render_ratio))
        self.rect3 = self.surf3.get_rect()
        self.surf4 = pygame.Surface((30 // render_ratio, 10 // render_ratio))
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

    def _process_collision_with_rect(self, rect, b_rect, b_speed, paddle_type):
        # handle collision from top
        if b_rect.bottom > rect.top and b_rect.top - b_speed[1] < rect.top and b_speed[1] > 0:
            b_rect.bottom = rect.top
            if b_speed[1] > 0:
                b_speed[1] *= -1
        # handle collision from bottom
        elif b_rect.top < rect.bottom and b_rect.bottom - b_speed[1] > rect.bottom and b_speed[1] < 0:
            b_rect.top = rect.bottom
            if b_speed[1] < 0:
                b_speed[1] *= -1
        # handle collision from left
        if b_rect.right > rect.left:
            b_rect.right = rect.left
            if b_speed[0] > 0:
                b_speed[0] *= -1
        return True, b_rect, b_speed

    def process_collision(self, b_rect, b_speed, paddle_type):
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
            return self._process_collision_with_rect(self.rect4, b_rect, b_speed, paddle_type)
        elif self.rect3.colliderect(b_rect):
            return self._process_collision_with_rect(self.rect3, b_rect, b_speed, paddle_type)
        elif self.rect2.colliderect(b_rect):
            return self._process_collision_with_rect(self.rect2, b_rect, b_speed, paddle_type)
        elif self.rect.colliderect(b_rect):
            return self._process_collision_with_rect(self.rect, b_rect, b_speed, paddle_type)
        return False, b_rect, b_speed
