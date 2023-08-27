from abc import  ABC

from agents.base import BaseAgent

from typing import Any, Optional

from memory.chatsummary import Memory
from type import ModelType

from models.base import ModelBackbone
from models.openai import ModelFactory

from config.gptconfig import ChatGPTConfig


class DebaterBase(BaseAgent, ABC):

    def __init__(self,
                 model: Optional[ModelType] = None,
                 model_config: Optional[Any] = None,
                 memory_prompt_path: Optional[Any] = None,
                 debater_base=None) -> None:
        """ Initialize the Agent Variables"""
        self.model = model

        """Initialize the Agent model"""
        if model_config:
            self.model_config = model_config

        else:
            self.model_config = ChatGPTConfig()

        self.model_backbone: ModelBackbone = ModelFactory.create(
            model_type=self.model)
        """Initialize the memory and chat message."""
        if memory_prompt_path is not None:
            self.memory = Memory(model_config= self.model_config,
                                 memory_prompt_path=memory_prompt_path,
                                 memory_type=debater_base)

    def reset(self):
        """ Reset the conversation Not the topic"""
        self.memory.chat_memory.messages[0].history = ""
        self.memory.chat_memory.messages[0].inputs = []

    @property
    def last_response(self):
        return self.memory.chat_memory.messages[0].inputs[-1]['assistant']

    @property
    def history(self):
        """ Keep the whole conversation history"""
        return self.memory.chat_memory.log[-1]
