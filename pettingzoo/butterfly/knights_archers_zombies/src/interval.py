"""Interval timer."""


class Interval:
    """Timer to mark every N steps.

    This is to make it easy to do an action every Nth step.
    It does not do that action, only flag when it should be done.
    The counter will automatically reset at once it reaches the
    Nth step, but it can be reset manually as needed.

    Parameters:
        step_interval: The interval frequency

    example usage:
    > interval = Interval(3)  # track every 3rd step
    > for i in range(6):
    >     if interval.increment():
    >         print("trigger at", i + 1)  # will be 3rd and 6th step (i=2,5)
    >     else:
    >         print("not triggered")
    not triggered
    not triggered
    trigger at 3
    not triggered
    not triggered
    trigger at 6
    """

    def __init__(self, step_interval: int) -> None:
        """Initialize the Interval object.

        Args:
            step_interval: how often the interval is True
        """
        self.step_interval = step_interval
        self._current_step = 0

    def increment(self) -> bool:
        """Increment the counter and return True and if it reached its interval.

        If the interval expired, it will be reset to its original value.
        """
        self._current_step += 1
        if self._current_step == self.step_interval:
            self.reset()
            return True
        return False

    def reset(self) -> None:
        """Reset the counter."""
        self._current_step = 0
