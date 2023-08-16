from __future__ import annotations

import logging
from logging import Logger
from typing import Any

import gymnasium.spaces


class EnvLogger:
    """Used for logging warnings and errors for environments."""

    mqueue: list[Any] = []
    _output: bool = True

    @staticmethod
    def get_logger() -> Logger:
        """Returns the logger object."""
        logger = logging.getLogger(__name__)
        return logger

    @staticmethod
    def _generic_warning(msg: Any) -> None:
        """Add a custom generic warning to the EnvLogger."""
        logger = EnvLogger.get_logger()
        if not logger.hasHandlers():
            handler = EnvWarningHandler(mqueue=EnvLogger.mqueue)
            logger.addHandler(handler)
        logger.warning(msg)
        # needed to get the pytest runner to work correctly, and doesn't seem to have serious issues
        EnvLogger.mqueue.append(msg)

    @staticmethod
    def flush() -> None:
        """Flushes EnvLogger output."""
        EnvLogger.mqueue.clear()

    @staticmethod
    def suppress_output() -> None:
        """Suppresses EnvLogger output."""
        EnvLogger._output = False

    @staticmethod
    def unsuppress_output() -> None:
        """Resets EnvLogger output to be printed."""
        EnvLogger._output = True

    @staticmethod
    def error_possible_agents_attribute_missing(name: str) -> None:
        """Warns: ``[ERROR]: This environment does not support {attribute}.``."""
        raise AttributeError(
            f"[ERROR]: This environment does not support {name}. This means that either the environment has procedurally generated agents such that this property cannot be well defined (which requires special learning code to handle) or the environment was improperly configured by the developer."
        )

    @staticmethod
    def warn_action_out_of_bound(
        action: Any, action_space: gymnasium.spaces.Space, backup_policy: str
    ) -> None:
        """Warns: ``[WARNING]: Received an action {action} that was outside action space {action_space}.``."""
        EnvLogger._generic_warning(
            f"[WARNING]: Received an action {action} that was outside action space {action_space}. Environment is {backup_policy}"
        )

    @staticmethod
    def warn_close_unrendered_env() -> None:
        """Warns: ``[WARNING]: Called close on an unrendered environment.``."""
        EnvLogger._generic_warning(
            "[WARNING]: Called close on an unrendered environment."
        )

    @staticmethod
    def warn_close_before_reset() -> None:
        """Warns: ``[WARNING]: reset() needs to be called before close.``."""
        EnvLogger._generic_warning(
            "[WARNING]: reset() needs to be called before close."
        )

    @staticmethod
    def warn_on_illegal_move() -> None:
        """Warns: ``[WARNING]: Illegal move made, game terminating with current player losing.``."""
        EnvLogger._generic_warning(
            "[WARNING]: Illegal move made, game terminating with current player losing. \nobs['action_mask'] contains a mask of all legal moves that can be chosen."
        )

    @staticmethod
    def error_observe_before_reset() -> None:
        """Error: ``reset() needs to be called before observe.``."""
        assert False, "reset() needs to be called before observe."

    @staticmethod
    def error_step_before_reset() -> None:
        """Error: ``reset() needs to be called before step.``."""
        assert False, "reset() needs to be called before step."

    @staticmethod
    def warn_step_after_terminated_truncated() -> None:
        """Warns: ``[WARNING]: step() called after all agents are terminated or truncated. Should reset() first.``."""
        EnvLogger._generic_warning(
            "[WARNING]: step() called after all agents are terminated or truncated. Should reset() first."
        )

    @staticmethod
    def error_render_before_reset() -> None:
        """Error: ``reset() needs to be called before render.``."""
        assert False, "reset() needs to be called before render."

    @staticmethod
    def error_agent_iter_before_reset() -> None:
        """Error: ``reset() needs to be called before agent_iter().``."""
        assert False, "reset() needs to be called before agent_iter()."

    @staticmethod
    def error_nan_action() -> None:
        """Error: ``step() cannot take in a nan action.``."""
        assert False, "step() cannot take in a nan action."

    @staticmethod
    def error_state_before_reset() -> None:
        """Error: ``reset() needs to be called before state.``."""
        assert False, "reset() needs to be called before state."


class EnvWarningHandler(logging.Handler):
    def __init__(self, *args, mqueue, **kwargs):
        logging.Handler.__init__(self, *args, **kwargs)
        self.mqueue = mqueue

    def emit(self, record: logging.LogRecord):
        m = self.format(record).rstrip("\n")
        self.mqueue.append(m)
        if EnvLogger._output:
            print(m)
