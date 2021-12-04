from ..capture_stdout import capture_stdout
from .base import BaseWrapper


class CaptureStdoutWrapper(BaseWrapper):
    def __init__(self, env):
        super().__init__(env)
        self.metadata['render.modes'].append("ansi")

    def render(self, mode="human"):
        if mode == "human":
            super().render(mode)
        elif mode == "ansi":
            with capture_stdout() as stdout:

                super().render(mode)

                val = stdout.getvalue()
            return val
        elif mode == "rgb_array":
            return super().render(mode)

    def __str__(self):
        return str(self.env)
