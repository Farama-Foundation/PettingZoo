from __future__ import annotations

from typing import Any


class agent_selector:
    """Outputs an agent in the given order whenever agent_select is called.

    Can reinitialize to a new order.

    Example:
        >>> from pettingzoo.utils import agent_selector
        >>> agent_selector = agent_selector(agent_order=["player1", "player2"])
        >>> agent_selector.reset()
        'player1'
        >>> agent_selector.next()
        'player2'
        >>> agent_selector.is_last()
        True
        >>> agent_selector.reinit(agent_order=["player2", "player1"])
        >>> agent_selector.next()
        'player2'
        >>> agent_selector.is_last()
        False
    """

    def __init__(self, agent_order: list[Any]):
        self.reinit(agent_order)

    def reinit(self, agent_order: list[Any]) -> None:
        """Reinitialize to a new order."""
        self.agent_order = agent_order
        self._current_agent = 0
        self.selected_agent = 0

    def reset(self) -> Any:
        """Reset to the original order."""
        self.reinit(self.agent_order)
        return self.next()

    def next(self) -> Any:
        """Get the next agent."""
        self._current_agent = (self._current_agent + 1) % len(self.agent_order)
        self.selected_agent = self.agent_order[self._current_agent - 1]
        return self.selected_agent

    def is_last(self) -> bool:
        """Check if the current agent is the last agent in the cycle."""
        return self.selected_agent == self.agent_order[-1]

    def is_first(self) -> bool:
        """Check if the current agent is the first agent in the cycle."""
        return self.selected_agent == self.agent_order[0]

    def __eq__(self, other: agent_selector) -> bool:
        if not isinstance(other, agent_selector):
            return NotImplemented

        return (
            self.agent_order == other.agent_order
            and self._current_agent == other._current_agent
            and self.selected_agent == other.selected_agent
        )
