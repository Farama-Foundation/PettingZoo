"""Spaces module for pettingzoo."""
from gym.spaces.box import Box
from gym.spaces.dict import Dict
from gym.spaces.discrete import Discrete
from gym.spaces.graph import Graph, GraphInstance
from gym.spaces.multi_binary import MultiBinary
from gym.spaces.multi_discrete import MultiDiscrete
from gym.spaces.sequence import Sequence
from gym.spaces.space import Space
from gym.spaces.text import Text
from gym.spaces.tuple import Tuple


__all__ = [
    "Space",
    "Box",
    "Discrete",
    "Text",
    "Graph",
    "GraphInstance",
    "MultiDiscrete",
    "MultiBinary",
    "Tuple",
    "Sequence",
    "Dict",
]
