from __future__ import annotations

from typing import Any
from warnings import warn

from typing_extensions import override


class AgentSelector:
    """Outputs an agent in the given order whenever agent_select is called.

    The selector owns its agent order: it copies the list it is given, rather
    than holding a reference to the caller's. An env whose agent set changes
    during an episode must therefore tell the selector about it, via
    :meth:`add_agent` and :meth:`remove_agent`, instead of mutating the list it
    passed to :meth:`reinit`. ``AECEnv._was_dead_step()`` already does this for
    agents it removes.

    Example:
        >>> from pettingzoo.utils import AgentSelector
        >>> agent_selector = AgentSelector(agent_order=["player1", "player2"])
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
        >>> agent_selector.add_agent("player3")
        >>> agent_selector.is_last()
        False
    """

    def __init__(self, agent_order: list[Any]):
        self.reinit(agent_order)

    def reinit(self, agent_order: list[Any]) -> None:
        """Reinitialize to a new order.

        The order is copied, so later mutations of ``agent_order`` by the caller
        do not silently change the cycle.
        """
        self.agent_order = list(agent_order)
        self._current_agent = 0
        self.selected_agent = 0

    def add_agent(self, agent: Any) -> None:
        """Add an agent to the end of the cycle."""
        self.agent_order.append(agent)

    def remove_agent(self, agent: Any) -> None:
        """Remove an agent from the cycle.

        Does nothing if the agent is not in the cycle, so that an env which has
        already dropped the agent itself can still call this unconditionally.
        """
        if agent in self.agent_order:
            self.agent_order.remove(agent)

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

    @override
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AgentSelector):
            return NotImplemented

        return (
            self.agent_order == other.agent_order
            and self._current_agent == other._current_agent
            and self.selected_agent == other.selected_agent
        )


class agent_selector(AgentSelector):
    """Deprecated version of AgentSelector. Use that instead."""

    def __init__(self, *args, **kwargs):
        warn(
            "agent_selector is deprecated, please use AgentSelector",
            DeprecationWarning,
        )
        super().__init__(*args, **kwargs)
