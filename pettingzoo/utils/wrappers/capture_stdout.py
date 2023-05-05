from pettingzoo.utils.capture_stdout import capture_stdout
from pettingzoo.utils.env import AECEnv
from pettingzoo.utils.wrappers.base import BaseWrapper


class CaptureStdoutWrapper(BaseWrapper):
    """Takes an environment which prints to terminal, and gives it an `ansi` render mode where it captures the terminal output and returns it as a string instead."""

    def __init__(self, env: AECEnv) -> None:
        assert hasattr(env, "render_mode"), f"Environment {env} has no render_mode."
        assert (
            env.render_mode == "human"  # type: ignore
        ), f"CaptureStdoutWrapper works only with human rendering mode, but found {env.render_mode} instead."  # type: ignore
        super().__init__(env)
        self.metadata["render_modes"].append("ansi")
        self.render_mode = "ansi"

    def render(self) -> str:
        with capture_stdout() as stdout:
            super().render()
            val = stdout.getvalue()
        return val

    def __str__(self) -> str:
        return str(self.env)
