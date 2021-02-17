from ..capture_stdout import capture_stdout
from .base import BaseWrapper


class CaptureStdoutWrapper(BaseWrapper):
    def __init__(self, env):
        super().__init__(env)
        self.metadata['render.modes'].append("ansi")

    def render(self, mode="human"):
        if mode == "human":
            super().render()
        elif mode == "ansi":
            with capture_stdout() as stdout:

                super().render()

                val = stdout.getvalue()
            return val

    def __str__(self):
        return str(self.env)
