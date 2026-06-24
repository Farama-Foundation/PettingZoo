"""Players used in Knights-Archers-Zombies."""

from __future__ import annotations

import os
from typing import Any

import pygame

from pettingzoo.butterfly.knights_archers_zombies.src import constants as const
from pettingzoo.butterfly.knights_archers_zombies.src.constants import Actions
from pettingzoo.butterfly.knights_archers_zombies.src.img import get_image
from pettingzoo.butterfly.knights_archers_zombies.src.interval import Interval
from pettingzoo.butterfly.knights_archers_zombies.src.mixins import VectorObservable
from pettingzoo.butterfly.knights_archers_zombies.src.weapons import Arrow, Sword


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

        # these are the limits of where the agent can move on the screen
        height = self.org_image.get_rect().height
        width = self.org_image.get_rect().width
        self.y_top_limit = height // 2
        self.y_bot_limit = const.SCREEN_HEIGHT - height // 2
        self.x_left_limit = const.WALL_WIDTH + width // 2
        self.x_right_limit = const.SCREEN_WIDTH - const.WALL_WIDTH - width // 2

        self.rect = pygame.Rect(0.0, 0.0, 0.0, 0.0)
        self.direction = pygame.Vector2(0, -1)

        self.is_alive = True
        self.score = 0

        self.speed = 0
        self.ang_rate = const.PLAYER_ANG_RATE

        self.timeout: None | Interval = None

        self.weapons: pygame.sprite.Group[Any] = pygame.sprite.Group()

    def is_timed_out(self, action: Actions) -> bool:
        """Return True if the Player is blocked from making the given action.

        It is up to the subclass to determine which actions are blocked.

        Args:
            action: The desired action
        """
        if self.timeout is None:
            return False
        if self.timeout.increment():  # timeout ended, remove block
            self.timeout = None
            return False
        return True

    def act(self, action: Actions) -> bool:
        """Perform the given action.

        This causes the player to move/turn/attack.
        It also checks that the player is within the bounds.
        If a move would take the player out of the box, it is instead
        moved to the edge and the out of bounds status is returned.

        Args:
            action: The action to perform

        Returns:
            whether or not the player is in the screen after acting
        """
        went_out_of_bounds = False

        if action == Actions.ACTION_FORWARD:
            self.rect.x += round(self.direction[0] * self.speed)
            self.rect.y += round(self.direction[1] * self.speed)
        elif action == Actions.ACTION_BACKWARD:
            self.rect.x -= round(self.direction[0] * self.speed)
            self.rect.y -= round(self.direction[1] * self.speed)
        elif action == Actions.ACTION_TURN_CCW:
            self.direction = self.direction.rotate(-self.ang_rate)
            self._update_image()
        elif action == Actions.ACTION_TURN_CW:
            self.direction = self.direction.rotate(self.ang_rate)
            self._update_image()
        elif action == Actions.ACTION_ATTACK and self.is_alive:
            self.attack()
        elif action == Actions.ACTION_NONE:
            pass

        # Clamp to stay inside the screen
        if self.rect.centery < self.y_top_limit or self.rect.centery > self.y_bot_limit:
            went_out_of_bounds = True

        self.rect.centerx = max(
            min(self.rect.centerx, self.x_right_limit), self.x_left_limit
        )
        self.rect.centery = max(
            min(self.rect.centery, self.y_bot_limit), self.y_top_limit
        )

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

    def attack(self) -> None:
        """Perform an attack."""


class Archer(Player):
    """Archer agent."""

    def __init__(self, agent_name: str) -> None:
        """Initialize an Archer.

        Args:
            agent_name: the name describing the agent
        """
        super().__init__(agent_name, "archer.png")
        self.rect = self.image.get_rect(center=(const.ARCHER_X, const.ARCHER_Y))
        self.speed = const.ARCHER_SPEED
        self.typemask = [0, 1, 0, 0, 0, 0]

    def is_timed_out(self, action: Actions) -> bool:
        """Return True if the Player is blocked from making the given move.

        Archers are blocked from attacking for a short time after attacking.
        """
        # only the attack action is blocked
        if action != Actions.ACTION_ATTACK:
            return False
        return super().is_timed_out(action)

    def attack(self) -> None:
        """Perform an attack.

        This adds a weapon to the knight which then attacks.
        It also sets a timeout on the archer's attack.
        """
        if self.timeout is not None:  # this should never happen
            raise RuntimeError("bad archer attack happened")
        self.timeout = Interval(const.ARROW_TIMEOUT)
        self.weapons.add(Arrow(self))


class Knight(Player):
    """Knight agent."""

    def __init__(self, agent_name: str) -> None:
        """Initialize a Knight.

        Args:
            agent_name: the name describing the agent
        """
        super().__init__(agent_name, "knight.png")
        self.rect = self.image.get_rect(center=(const.KNIGHT_X, const.KNIGHT_Y))
        self.speed = const.KNIGHT_SPEED
        self.typemask = [0, 0, 1, 0, 0, 0]

    def attack(self) -> None:
        """Perform an attack.

        This adds a weapon to the knight which then attacks.
        """
        if self.timeout is not None:  # this should never happen
            raise RuntimeError("bad knight attack happened - timeout")
        # make sure that the knight doesn't have a sword already
        if len(self.weapons) == 0:
            self.weapons.add(Sword(self))
            self.timeout = Interval(const.KNIGHT_TIMEOUT)
        else:  # this should never happen
            raise RuntimeError("bad knight attack happened - already attacking")


def is_archer(player: Player) -> bool:
    """Return True if the player is an archer."""
    return isinstance(player, Archer)


def is_knight(player: Player) -> bool:
    """Return True if the player is a knight."""
    return isinstance(player, Knight)
