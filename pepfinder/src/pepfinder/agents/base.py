"""Base agent interfaces."""

from abc import ABC, abstractmethod


class BaseAgent(ABC):
    """Abstract interface for a pipeline agent."""

    @abstractmethod
    def run(self, *args, **kwargs):
        """Execute the agent's primary behavior."""
