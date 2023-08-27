from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Optional, Any

from colorama import Style, Fore

from config.palmconfig import PaLMConfig
from type import ModelType
from config.gptconfig import ChatGPTConfig
from memory.base import BaseChatMessageHistory, BaseChatMemory
from models.base import ModelBackbone
from models.openai import ModelFactory
from utils import *

import tiktoken

enc = tiktoken.encoding_for_model("gpt-4")


class Memory(BaseChatMemory, ABC):
    def __init__(self, memory_prompt_path=None, model_config: Optional[Any] = None, memory_type=None):
        self.model_config: ChatGPTConfig = ChatGPTConfig()
        self.model_backbone: ModelBackbone = ModelFactory.create(
            model_type=ModelType.GPT_3_5_TURBO_0301)
        self.message_to_summarize: BaseChatMessageHistory = BaseChatMessageHistory()
        self.memory_prompt_path = memory_prompt_path
        self.memory_type = memory_type
        super().__init__()
        self.limit_number=4050

    def to_summarize(self):

        size = len(self.chat_memory.messages[-1].inputs)
        self.chat_memory.messages.append(deepcopy(self.chat_memory.messages[-1]))

        if size > 11:
            print(Fore.RED + '****Get summary of 11******' + Style.RESET_ALL)
            print(Fore.RED + '****Get summary of 11******' + Style.RESET_ALL)
            if self.memory_type == "PersuaderAgent":
                self.chat_memory.messages[1].inputs = [deepcopy(self.chat_memory.messages[0].inputs[0])] + \
                                                      deepcopy(self.chat_memory.messages[
                                                                   0].inputs[-9:])
                self.message_to_summarize = deepcopy(self.chat_memory.messages[0])
                self.message_to_summarize.inputs = deepcopy(self.chat_memory.messages[0].inputs[1:-9])
            else:
                self.chat_memory.messages[1].inputs = [deepcopy(self.chat_memory.messages[0].inputs[0])] + \
                                                      deepcopy(self.chat_memory.messages[
                                                                   0].inputs[-8:])
                self.message_to_summarize = deepcopy(self.chat_memory.messages[0])
                self.message_to_summarize.inputs = deepcopy(self.chat_memory.messages[0].inputs[1:-8])
        elif size > 9:
            print(Fore.YELLOW + '****Get summary of 7******' + Style.RESET_ALL)
            if self.memory_type == "!PersuaderAgent":
                self.chat_memory.messages[1].inputs = [self.chat_memory.messages[0].inputs[0]] + \
                                                      self.chat_memory.messages[
                                                          0].inputs[-7:]
                self.message_to_summarize = deepcopy(self.chat_memory.messages[0])
                self.message_to_summarize.inputs = self.chat_memory.messages[0].inputs[1:-7]
            else:
                self.chat_memory.messages[1].inputs = [self.chat_memory.messages[0].inputs[0]] + \
                                                      self.chat_memory.messages[
                                                          0].inputs[-6:]
                self.message_to_summarize = deepcopy(self.chat_memory.messages[0])
                self.message_to_summarize.inputs = self.chat_memory.messages[0].inputs[1:-6]
        elif size > 7:
            print(Fore.YELLOW + '****Get summary of 7******' + Style.RESET_ALL)
            if self.memory_type == "PersuaderAgent":
                self.chat_memory.messages[1].inputs = [self.chat_memory.messages[0].inputs[0]] + \
                                                      self.chat_memory.messages[
                                                          0].inputs[-5:]
                self.message_to_summarize = deepcopy(self.chat_memory.messages[0])
                self.message_to_summarize.inputs = self.chat_memory.messages[0].inputs[1:-5]
            else:
                self.chat_memory.messages[1].inputs = [self.chat_memory.messages[0].inputs[0]] + \
                                                      self.chat_memory.messages[
                                                          0].inputs[-4:]
                self.message_to_summarize = deepcopy(self.chat_memory.messages[0])
                self.message_to_summarize.inputs = self.chat_memory.messages[0].inputs[1:-4]
        elif size > 5:
            print(Fore.YELLOW + '****Get summary of 5******' + Style.RESET_ALL)
            if self.memory_type == "PersuaderAgent":
                self.chat_memory.messages[1].inputs = [self.chat_memory.messages[0].inputs[0]] + \
                                                      self.chat_memory.messages[
                                                          0].inputs[-3:]
                self.message_to_summarize = deepcopy(self.chat_memory.messages[0])
                self.message_to_summarize.inputs = self.chat_memory.messages[0].inputs[1:-3]
            else:
                self.chat_memory.messages[1].inputs = [self.chat_memory.messages[0].inputs[0]] + \
                                                      self.chat_memory.messages[
                                                          0].inputs[-2:]
                self.message_to_summarize = deepcopy(self.chat_memory.messages[0])
                self.message_to_summarize.inputs = self.chat_memory.messages[0].inputs[1:-2]

        else:
            print(Fore.YELLOW + '****Get summary of 2******' + Style.RESET_ALL)
            self.chat_memory.messages[1].inputs = [deepcopy(self.chat_memory.messages[0].inputs[0])]

            self.message_to_summarize = deepcopy(self.chat_memory.messages[0])
            self.message_to_summarize.inputs = deepcopy(self.chat_memory.messages[0].inputs[2:])

    def generate_summary(self):

        self.to_summarize()
        variables = {"<HISTORY>": self.message_to_summarize.history,
                     "<ASSISTANT-USER>": self.message_to_summarize.inputs}
        system, user = extract_prompt(self.memory_prompt_path, variables)
        prompt = [{'role': 'system', 'content': system}, {'role': 'user', 'content': user}]
        response = self.model_backbone.run( messages=prompt)
        print(Fore.YELLOW + '****Generated summary******' + Style.RESET_ALL)
        print(response)
        self.chat_memory.messages[1].history = str(response)
        self.clear()
        self.check_token_limit()

    def check_token_limit(self):
        """check history, if over limit, then summarize"""

        if self.limit_number < len(enc.encode(str(self.generate_prompt()))):
            print("******* Generating Summary******")
            self.generate_summary()

    def memory(self):
        """ Return the most recent messages if token limit not exceeds """
        return self.chat_memory.messages[-1]

    def prompt(self):
        self.check_token_limit()

        return self.generate_prompt()

    def generate_prompt(self):
        if self.chat_memory.messages[0].history != "":

            formatted_memory = {
                "role": "system",
                "content": self.chat_memory.log[0].system + "The previous history is: " + self.chat_memory.messages[
                    0].history + "Now lets start the debate:"
            }
            self.chat_memory.messages[0].system = formatted_memory["content"]

        else:

            formatted_memory = {
                "role": "system",
                "content": self.chat_memory.log[0].system + "Now lets start the debate:"
            }

        formatted_messages = []
        for message in self.chat_memory.messages:
            for input_message in message.inputs:
                role = next(iter(input_message))
                content = input_message[role]
                formatted_message = {"role": role, "content": content}
                formatted_messages.append(formatted_message)
        return [
            formatted_memory,
            *formatted_messages
        ]

    def clear(self) -> None:
        """ Clear previous messages after summarization"""
        self.chat_memory.messages.pop(0)
