from __future__ import annotations

from typing import Any


class agent_selector:
    """Outputs an agent in the given order whenever agent_select is called.

    Can reinitialize to a new order
    """

    def __init__(self, agent_order: list[Any]):
        self.reinit(agent_order)

    def reinit(self, agent_order: list[Any]) -> None:
        self.agent_order = agent_order
        self._current_agent = 0
        self.selected_agent = 0

    def reset(self) -> Any:
        self.reinit(self.agent_order)
        return self.next()

    def next(self) -> Any:
        self._current_agent = (self._current_agent + 1) % len(self.agent_order)
        self.selected_agent = self.agent_order[self._current_agent - 1]
        return self.selected_agent

    def is_last(self) -> bool:
        """Does not work as expected if you change the order."""
        return self.selected_agent == self.agent_order[-1]

    def is_first(self) -> bool:
        return self.selected_agent == self.agent_order[0]

    def __eq__(self, other: agent_selector) -> bool:
        if not isinstance(other, agent_selector):
            return NotImplemented

        return (
            self.agent_order == other.agent_order
            and self._current_agent == other._current_agent
            and self.selected_agent == other.selected_agent
        )
