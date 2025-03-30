import warnings

from pettingzoo.mpe.simple_speaker_listener.simple_speaker_listener import (
    env,
    parallel_env,
    raw_env,
)

warnings.warn(
    "The environment `pettingzoo.mpe.speaker_listener_v4` has been moved to `mpe2.simple_speaker_listener_v4` and will be removed in a future release. "
    "Please update your imports.",
    DeprecationWarning,
    stacklevel=2,
)


__all__ = ["env", "parallel_env", "raw_env"]
