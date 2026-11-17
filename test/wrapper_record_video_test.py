from __future__ import annotations

import os
import shutil

import numpy as np
import pytest

from pettingzoo.butterfly import pistonball_v6
from pettingzoo.utils import parallel_to_aec
from pettingzoo.utils.wrappers import (
    BaseParallelWrapper,
    RecordVideo,
    RecordVideoParallel,
)


def test_video_folder_and_filenames_base(
    video_folder="custom_video_folder/aec", name_prefix="video-prefix"
):
    par_env = pistonball_v6.parallel_env(render_mode="rgb_array", max_cycles=30)
    aec_env = parallel_to_aec(par_env)
    env = RecordVideo(
        aec_env,
        video_folder=video_folder,
        name_prefix=name_prefix,
        episode_trigger=lambda x: x in [1, 4],
        step_trigger=lambda x: x in [0, 25],
    )

    for _ in range(130):
        env.reset(seed=123)

        for agent in env.agent_iter():
            obs, reward, terminated, truncated, info = env.last()
            action = (
                None if (terminated or truncated) else env.action_space(agent).sample()
            )
            env.step(action)  # type: ignore

    env.close()

    assert os.path.isdir(video_folder)
    mp4_files = {file for file in os.listdir(video_folder) if file.endswith(".mp4")}
    shutil.rmtree(video_folder)
    assert mp4_files == {
        "video-prefix-step-0.mp4",  # step triggers
        "video-prefix-step-25.mp4",
        "video-prefix-episode-1.mp4",  # episode triggers
        "video-prefix-episode-4.mp4",
    }


def test_video_folder_and_filenames_parallel(
    video_folder="custom_video_folder/parallel", name_prefix="video-prefix"
):
    par_env = pistonball_v6.parallel_env(render_mode="rgb_array", max_cycles=30)
    env = RecordVideoParallel(
        par_env,
        video_folder=video_folder,
        name_prefix=name_prefix,
        episode_trigger=lambda x: x in [1, 4],
        step_trigger=lambda x: x in [0, 25],
    )

    obs, infos = env.reset(seed=123)
    for _ in range(130):
        actions = {agent: env.action_space(agent).sample() for agent in obs}
        obs, rewards, terms, truncs, infos = env.step(actions)
        if any(terms.values()) or any(truncs.values()):
            obs, infos = env.reset()

    env.close()

    assert os.path.isdir(video_folder)
    mp4_files = {file for file in os.listdir(video_folder) if file.endswith(".mp4")}
    shutil.rmtree(video_folder)
    assert mp4_files == {
        "video-prefix-step-0.mp4",  # step triggers
        "video-prefix-step-25.mp4",
        "video-prefix-episode-1.mp4",  # episode triggers
        "video-prefix-episode-4.mp4",
    }


@pytest.mark.parametrize(
    "wrapper,env_fn",
    [
        (RecordVideo, lambda: parallel_to_aec(pistonball_v6.parallel_env())),
        (RecordVideoParallel, lambda: pistonball_v6.parallel_env()),
    ],
)
def test_incompatible_render_mode(wrapper, env_fn):
    """Construction with a render mode that yields no image fails cleanly.

    The message used to be split across two arguments of `ValueError`, so
    `str(e)` printed a tuple and the sentence telling the user what to do
    arrived quoted inside it. `__del__` then ran on the half-built wrapper and
    raised an AttributeError of its own, which Python reports as an ignored
    exception on top of the real one.
    """
    env = env_fn()  # render_mode is None

    with pytest.raises(ValueError) as exc_info:
        wrapper(env, video_folder="videos")

    assert len(exc_info.value.args) == 1
    assert "such as rgb_array" in str(exc_info.value)

    # `__del__` runs on the object the failed `__init__` left behind. At the
    # point of the raise, `super().__init__(env)` had assigned `env` and nothing
    # else, so that is the whole state to reproduce.
    half_built = wrapper.__new__(wrapper)
    half_built.env = env
    half_built.__del__()


class ReusableRenderBuffer(BaseParallelWrapper):
    """Render real Pistonball frames into a reusable output buffer."""

    def __init__(self, env, as_list):
        super().__init__(env)
        self.as_list = as_list
        self.buffer = None
        self.render_mode = "rgb_array_list" if as_list else "rgb_array"
        self.metadata = {**env.metadata, "render_modes": [self.render_mode]}

    def render(self):
        frame = self.env.render()
        if self.buffer is None:
            self.buffer = np.empty_like(frame)
        np.copyto(self.buffer, frame)
        return [self.buffer] if self.as_list else self.buffer


@pytest.mark.parametrize("parallel", [False, True])
@pytest.mark.parametrize("as_list", [False, True])
def test_record_video_preserves_reused_render_buffers(tmp_path, parallel, as_list):
    par_env = ReusableRenderBuffer(
        pistonball_v6.parallel_env(n_pistons=3, render_mode="rgb_array", max_cycles=20),
        as_list=as_list,
    )
    base = par_env if parallel else parallel_to_aec(par_env)
    wrapper = RecordVideoParallel if parallel else RecordVideo
    env = wrapper(
        base,
        video_folder=str(tmp_path / "video"),
        episode_trigger=lambda _: True,
        gc_trigger=None,
    )
    try:
        env.reset(seed=123)
        expected = [par_env.buffer.copy()]
        for _ in range(8):
            action = np.array([1.0], dtype=np.float32)
            env.step(dict.fromkeys(env.agents, action) if parallel else action)
            expected.append(par_env.buffer.copy())

        # The physical scene changed; retained frames must not all become its
        # final state when the renderer overwrites its output array.
        assert not np.array_equal(expected[0], expected[-1])
        np.testing.assert_array_equal(env.recorded_frames, expected)
        assert not np.shares_memory(env.recorded_frames[0], par_env.buffer)

        rendered = env.render()
        if as_list:
            np.testing.assert_array_equal(rendered, [*expected, expected[-1]])
            np.testing.assert_array_equal(
                env.recorded_frames, [*expected, expected[-1]]
            )
            # Neither the returned history nor the current render result is
            # allowed to mutate frames already retained for the video.
            for frame in rendered:
                frame.fill(0)
            np.testing.assert_array_equal(
                env.recorded_frames, [*expected, expected[-1]]
            )
        else:
            assert rendered is par_env.buffer
    finally:
        env.close()


@pytest.mark.parametrize("parallel", [False, True])
def test_record_video_snapshots_explicit_list_render(tmp_path, parallel):
    par_env = ReusableRenderBuffer(
        pistonball_v6.parallel_env(n_pistons=3, render_mode="rgb_array"),
        as_list=True,
    )
    base = par_env if parallel else parallel_to_aec(par_env)
    wrapper = RecordVideoParallel if parallel else RecordVideo
    env = wrapper(
        base,
        video_folder=str(tmp_path / "video"),
        episode_trigger=lambda _: False,
        gc_trigger=None,
    )
    try:
        env.reset(seed=123)
        assert env.render_history == []
        env.start_recording("explicit-render")
        rendered = env.render()
        expected = rendered[0].copy()
        rendered[0].fill(0)
        np.testing.assert_array_equal(env.recorded_frames, [expected])
    finally:
        env.close()
