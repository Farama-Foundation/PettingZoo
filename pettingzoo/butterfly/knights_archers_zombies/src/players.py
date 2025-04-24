"""Players used in Knights-Archers-Zombies."""

import os
from typing import Any

import pygame

from pettingzoo.butterfly.knights_archers_zombies.src import constants as const
from pettingzoo.butterfly.knights_archers_zombies.src.constants import Actions
from pettingzoo.butterfly.knights_archers_zombies.src.img import get_image
from pettingzoo.butterfly.knights_archers_zombies.src.mixins import VectorObservable


class Player(pygame.sprite.Sprite, VectorObservable):
    """Base class for a player's agent."""

    def __init__(self, agent_name: str, image_name: str) -> None:
        """Initialize a Player.

        Args:
            agent_name: name of the agent
            image_name: filename of icon for agent
        """
        super().__init__()
        self.agent_name = agent_name
        self.image = get_image(os.path.join("img", image_name))
        self.org_image = self.image.copy()

        self.rect = pygame.Rect(0.0, 0.0, 0.0, 0.0)
        self.direction = pygame.Vector2(0, -1)

        self.is_alive = True
        self.score = 0

        self.is_archer = False
        self.is_knight = False

        self.speed = 0
        self.ang_rate = const.PLAYER_ANG_RATE

        self.action = Actions.ActionNone
        self.attacking = False
        self.weapon_timeout = 99

        self.weapons: pygame.sprite.Group[Any] = pygame.sprite.Group()

    def act(self, action: Actions) -> bool:
        """Perform the given action.

        This moves/turns the player. Attacks are handled elsewhere.
        It also checks that the player is within the bounds.
        If a move would take the player out of the box, it is instead
        moved to the edge and the out of bounds status is returned.

        Args:
            action: The action to perform

        Returns:
            whether or not the player is in the screen after acting
        """
        self.action = action
        went_out_of_bounds = False

        if not self.attacking:
            if action == Actions.ActionForward and self.rect.y > 20:
                self.rect.x += round(self.direction[0] * self.speed)
                self.rect.y += round(self.direction[1] * self.speed)
            elif (
                action == Actions.ActionBackward
                and self.rect.y < const.SCREEN_HEIGHT - 40
            ):
                self.rect.x -= round(self.direction[0] * self.speed)
                self.rect.y -= round(self.direction[1] * self.speed)
            elif action == Actions.ActionTurnCCW:
                self.direction = self.direction.rotate(-self.ang_rate)
                self._update_image()
            elif action == Actions.ActionTurnCW:
                self.direction = self.direction.rotate(self.ang_rate)
                self._update_image()
            elif action == Actions.ActionAttack and self.is_alive:
                pass
            elif action == Actions.ActionNone:
                pass

            # Clamp to stay inside the screen
            if self.rect.y < 0 or self.rect.y > (const.SCREEN_HEIGHT - 40):
                went_out_of_bounds = True

            self.rect.x = max(min(self.rect.x, const.SCREEN_WIDTH - 132), 100)
            self.rect.y = max(min(self.rect.y, const.SCREEN_HEIGHT - 40), 0)

            # add to weapon timeout when we know we're not attacking
            self.weapon_timeout += 1
        else:
            self.weapon_timeout = 0

        return went_out_of_bounds

    def _update_image(self) -> None:
        """Update the image after rotating."""
        angle = self.direction.angle_to(pygame.Vector2(0, -1))
        self.image = pygame.transform.rotate(self.org_image, angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def offset(self, x_offset: int, y_offset: int) -> None:
        """Move the object by the given offsets."""
        self.rect.x += x_offset
        self.rect.y += y_offset

    def is_done(self) -> bool:
        """Return True if the agent is not alive."""
        return not self.is_alive


class Archer(Player):
    """Archer agent."""

    def __init__(self, agent_name: str) -> None:
        """Initialize an Archer.

        Args:
            agent_name: the name describing the agent
        """
        super().__init__(agent_name, "archer.png")
        self.rect = self.image.get_rect(center=(const.ARCHER_X, const.ARCHER_Y))
        self.is_archer = True
        self.speed = const.ARCHER_SPEED
        self.typemask = [0, 1, 0, 0, 0, 0]


class Knight(Player):
    """Knight agent."""

    def __init__(self, agent_name: str) -> None:
        """Initialize a Knight.

        Args:
            agent_name: the name describing the agent
        """
        super().__init__(agent_name, "knight.png")
        self.rect = self.image.get_rect(center=(const.KNIGHT_X, const.KNIGHT_Y))
        self.is_knight = True
        self.speed = const.KNIGHT_SPEED
        self.typemask = [0, 0, 1, 0, 0, 0]
