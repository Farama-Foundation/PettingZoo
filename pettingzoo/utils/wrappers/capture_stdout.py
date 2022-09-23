from ..capture_stdout import capture_stdout
from .base import BaseWrapper


class CaptureStdoutWrapper(BaseWrapper):
    def __init__(self, env):
        assert (
            env.render_mode == "human"
        ), f"CaptureStdoutWrapper works only with human rendering mode, but found {env.render_mode} instead."
        super().__init__(env)
        self.metadata["render_modes"].append("ansi")
        self.render_mode = "ansi"

    def render(self):
        with capture_stdout() as stdout:
            super().render()
            val = stdout.getvalue()
        return val

    def __str__(self):
        return str(self.env)
