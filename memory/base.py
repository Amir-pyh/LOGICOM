from abc import ABC, abstractmethod
from typing import List

from dataclasses import dataclass, field


@dataclass
class BaseChatMessage:
    system: str
    history: str
    inputs: List[dict] = field(default_factory=list)


@dataclass
class BaseChatMessageHistory:
    messages: List[BaseChatMessage] = field(default_factory=list)
    log: List[BaseChatMessage] = field(default_factory=list)

    def __post_init__(self):
        if not self.messages:
            self.messages.append(BaseChatMessage(system="", history="", inputs=[]))


class BaseChatMemory(ABC):
    def __init__(self):
        self.chat_memory: BaseChatMessageHistory = BaseChatMessageHistory()

    def add_user_message(self, message: str) -> None:
        user_message = {"user": message}
        self.chat_memory.messages[-1].inputs.append(user_message)

        self.chat_memory.log[-1].inputs.append(user_message)

    def add_ai_message(self, message: str, fallacy_type=None) -> None:
        ai_message = {"assistant": message}
        self.chat_memory.messages[-1].inputs.append(ai_message)
        if fallacy_type:
            ai_message = {"assistant": str([fallacy_type])}
            self.chat_memory.log[-1].inputs.append(ai_message)
        else:
            self.chat_memory.log[-1].inputs.append(ai_message)

    @abstractmethod
    def memory(self) -> BaseChatMessageHistory:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass

    @abstractmethod
    def prompt(self):
        pass
