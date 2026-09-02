from typing_extensions import override

from pettingzoo.utils.capture_stdout import capture_stdout
from pettingzoo.utils.env import ActionType, AECEnv, AgentID, ObsType
from pettingzoo.utils.wrappers.base import BaseWrapper


class CaptureStdoutWrapper(BaseWrapper[AgentID, ObsType, ActionType]):
    """Takes an environment which prints to terminal, and gives it an `ansi` render mode where it captures the terminal output and returns it as a string instead."""

    def __init__(self, env: AECEnv[AgentID, ObsType, ActionType]):
        assert isinstance(env, AECEnv), (
            "CaptureStdoutWrapper is only compatible with AEC environments"
        )
        assert hasattr(env, "render_mode"), f"Environment {env} has no render_mode."
        assert env.render_mode == "human", (
            f"CaptureStdoutWrapper works only with human rendering mode, but found {env.render_mode} instead."
        )
        super().__init__(env)
        # `metadata` is a class attribute on the wrapped environment, so mutating
        # it in place would add "ansi" to every instance of that environment for
        # the lifetime of the process. Shadow it with a per-wrapper copy instead.
        self.metadata = {
            **self.env.metadata,
            "render_modes": [*self.env.metadata["render_modes"], "ansi"],
        }
        self.render_mode = "ansi"

    @override
    def render(self) -> str:
        with capture_stdout() as stdout:
            super().render()
            val = stdout.getvalue()
        return val

    @override
    def __str__(self) -> str:
        return str(self.env)
