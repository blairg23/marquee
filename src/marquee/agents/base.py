"""Provider-agnostic agent interface. No vendor SDK belongs in business logic.

M2 (#14). Not implemented yet -- this is the shape M2 will fill in.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Agent(ABC):
    """Base class every judgment stage (director, designer, critic) implements."""

    @abstractmethod
    def run(self, **inputs: Any) -> Any:
        """Execute this agent's judgment step and return its structured output."""
        raise NotImplementedError
