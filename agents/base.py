from abc import ABC, abstractmethod


class BaseAgent(ABC):
    r"""The base agent abstract class"""

    @abstractmethod
    def reset(self) -> None:
        r"""Resets the agent to its initial state."""
        pass

    @abstractmethod
    def helper_feedback(self) -> None:
        r"""receives argumentative helps"""
        pass

    @abstractmethod
    def call(self, message):
        pass
