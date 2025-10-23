from __future__ import annotations

import gc
import os
from typing import Any, Callable, TypeAlias

import gymnasium
import numpy as np
from gymnasium.error import DependencyNotInstalled

from pettingzoo.utils.env import ActionType, AECEnv, AgentID
from pettingzoo.utils.wrappers.base import BaseWrapper

RenderFrame: TypeAlias = np.typing.NDArray[Any]


class RecordVideo(BaseWrapper):
    def __init__(
        self,
        env: AECEnv,
        video_folder: str,
        episode_trigger: Callable[[int], bool] | None = None,
        step_trigger: Callable[[int], bool] | None = None,
        video_length: int = 0,
        name_prefix: str = "rl-video",
        fps: int | None = None,
        disable_logger: bool = True,
        gc_trigger: Callable[[int], bool] | None = lambda episode: True,
    ):
        """Wraps an AEC environment with to output interval-based recordings.

        Args:
            env (ParallelEnv): The parallel environment that will be trapped.
            video_folder (str): The folder where the recordings will be stored.
            episode_trigger (Callable[[int], bool] | None, optional): Function that accepts an integer and returns
              ``True`` to start recording an episode.
            step_trigger (Callable[[int], bool] | None, optional): Function that accepts an integer that should return
                ``True`` on the n-th environment step that the recording should be started,
                where n sums over all previous episodes.
            video_length (int, optional): The length of recorded episodes. If 0, entire episodes are recorded.
                Otherwise, snippets of the specified length are captured.
            name_prefix (str, optional): Will be prepended to the filename of the recordings. Defaults to "rl-video".
            fps (int | None, optional): The frame per second in the video. Provides a custom video fps for environment,
                if ``None`` then the environment metadata ``render_fps`` key is used if it exists,
                otherwise a default value of 30 is used.
            disable_logger (bool, optional): Whether to disable moviepy logger or not, default it is disabled
            gc_trigger (_type_, optional):  Function that accepts an integer and returns ``True`` iff garbage
                collection should be performed after this episode

        Raises:
            ValueError: If the render_mode is not suitable, an image must be returned per render step
            DependencyNotInstalled: If `MoviePy` is not installed
        """
        super().__init__(env)
        assert isinstance(
            env, AECEnv
        ), "RecordVideoEnv is only compatible with AECEnv environments."

        if env.render_mode in {None, "human", "ansi"}:  # type: ignore
            raise ValueError(
                f"Render mode is {env.render_mode}, which is incompatible with RecordVideo.",  # type: ignore
                "Initialize your environment with a render_mode that returns an image, such as rgb_array.",
            )

        if episode_trigger is None and step_trigger is None:
            episode_trigger = (
                lambda episode_id: (
                    int(round(episode_id ** (1.0 / 3))) ** 3 == episode_id
                )
                if episode_id < 1000
                else (episode_id % 1000 == 0)
            )

        self.episode_trigger = episode_trigger
        self.step_trigger = step_trigger
        self.disable_logger = disable_logger
        self.gc_trigger = gc_trigger

        self.video_folder = os.path.abspath(video_folder)
        if os.path.isdir(self.video_folder):
            gymnasium.logger.warn(
                f"Overwriting existing videos at {self.video_folder} folder "
                f"(try specifying a different `video_folder` for the `RecordVideo` wrapper if this is not desired)"
            )
        os.makedirs(self.video_folder, exist_ok=True)

        if fps is None:
            fps = int(getattr(env, "metadata", {}).get("render_fps", 30))
        self.frames_per_sec: int = fps
        self.name_prefix: str = name_prefix
        self._video_name: str | None = None
        self.video_length: int | float = (
            video_length if video_length != 0 else float("inf")
        )
        self.recording: bool = False
        self.recorded_frames: list[RenderFrame] = []
        self.render_history: list[RenderFrame] = []

        self.step_id: int = -1
        self.episode_id: int = -1

        try:
            import moviepy  # noqa: F401
        except ImportError as e:
            raise DependencyNotInstalled(
                'MoviePy is not installed, run `pip install "pettingzoo[other]"`'
            ) from e

    def _capture_frame(self):
        assert self.recording, "Cannot capture a frame, recording wasn't started."

        frame = self.env.render()
        if isinstance(frame, list):
            if len(frame) == 0:
                return
            self.render_history += frame
            frame = frame[-1]

        if isinstance(frame, np.ndarray):
            self.recorded_frames.append(frame)
        else:
            self.stop_recording()
            gymnasium.logger.warn(
                f"Recording stopped: expected type of frame returned by render to be a numpy array, got instead {type(frame)}."
            )

    def reset(self, seed: int | None = None, options: dict | None = None) -> None:
        """Reset the environment and eventually starts a new recording."""
        self.env.reset(seed=seed, options=options)
        self.episode_id += 1

        if self.recording and self.video_length == float("inf"):
            self.stop_recording()

        if self.episode_trigger and self.episode_trigger(self.episode_id):
            self.start_recording(f"{self.name_prefix}-episode-{self.episode_id}")
        if self.recording:
            self._capture_frame()
            if len(self.recorded_frames) > self.video_length:
                self.stop_recording()

    def step(self, actions: dict[AgentID, ActionType]) -> None:
        """Steps through the environment using actions, recording frames if `self.recording`."""
        self.env.step(actions)
        self.step_id += 1

        if self.step_trigger and self.step_trigger(self.step_id):
            self.start_recording(f"{self.name_prefix}-step-{self.step_id}")
        if self.recording:
            self._capture_frame()

            if len(self.recorded_frames) > self.video_length:
                self.stop_recording()

    def render(self):
        """Compute the render frames as specified by render_mode attribute during initialization of the environment."""
        render_out = self.env.render()
        if self.recording and isinstance(render_out, list):
            self.recorded_frames += render_out

        if len(self.render_history) > 0:
            tmp_history = self.render_history
            self.render_history = []
            frames = render_out if isinstance(render_out, list) else [render_out]
            return tmp_history + frames
        else:
            return render_out

    def close(self):
        """Closes the wrapper then the video recorder."""
        super().close()
        if self.recording:
            self.stop_recording()

    def start_recording(self, video_name: str):
        """Start a new recording. If it is already recording, stops the current recording before starting the new one."""
        if self.recording:
            self.stop_recording()

        self.recording = True
        self._video_name = video_name

    def stop_recording(self):
        """Stop current recording and saves the video."""
        assert self.recording, "stop_recording was called, but no recording was started"

        if len(self.recorded_frames) == 0:
            gymnasium.logger.warn(
                "Ignored saving a video as there were zero frames to save."
            )
        else:
            try:
                from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
            except ImportError as e:
                raise DependencyNotInstalled(
                    'MoviePy is not installed, run `pip install "pettingzoo[other]"`'
                ) from e

            clip = ImageSequenceClip(self.recorded_frames, fps=self.frames_per_sec)
            moviepy_logger = None if self.disable_logger else "bar"
            path = os.path.join(self.video_folder, f"{self._video_name}.mp4")
            clip.write_videofile(path, logger=moviepy_logger)

        self.recorded_frames = []
        self.recording = False
        self._video_name = None

        if self.gc_trigger and self.gc_trigger(self.episode_id):
            gc.collect()

    def __del__(self):
        """Warn the user in case last video wasn't saved."""
        if len(self.recorded_frames) > 0:
            gymnasium.logger.warn("Unable to save last video! Did you call close()?")
