from abc import ABC
from typing import Any, Dict, Optional
from tenacity import retry, stop_after_attempt, wait_chain, wait_fixed
from agents.base import BaseAgent
from agents.moderatorResponse import ModeratorResponse
from config.gptconfig import ChatGPTConfig
from models.base import ModelBackbone
from models.openai import ModelFactory
from type import  ModelType, ModeratorInfo, SignalType
from utils import extract_prompt
import re

class ModeratorAgent(BaseAgent, ABC):
    def __init__(self,
                 model: Optional[ModelType] = None,
                 model_config: Optional[Any] = None,
                 prompt_instruction_path_moderator_terminator=None,
                 prompt_instruction_path_moderator_tag_checker=None,
                 prompt_instruction_path_moderator_topic_checker=None,
                 variables: Optional[Dict] = None,
                 ) -> None:
        self.topic_check = None
        self.signal_check = None
        self.persuader_recent_history_last = None
        self.model = model
        self.variables = variables
        self.system_instruction_terminator, _ = extract_prompt(prompt_instruction_path_moderator_terminator, self.variables)
        self.system_instruction_tag_checker, _ = extract_prompt(prompt_instruction_path_moderator_tag_checker, self.variables)
        self.system_instruction_topic_checker, _ = extract_prompt(prompt_instruction_path_moderator_topic_checker,
                                                                self.variables)
        self.system_instruction = [self.system_instruction_terminator, self.system_instruction_tag_checker, self.system_instruction_topic_checker]

        self.model_config: ChatGPTConfig = model_config or ChatGPTConfig()
        self.model_backbone: ModelBackbone = ModelFactory.create(model_type=self.model)

        self.not_convinced_counter = 0
        self.keep_talking = None
        self.terminate = None

    def reset(self):
        pass

    @retry(stop=stop_after_attempt(5),
           wait=wait_chain(*[wait_fixed(2) for i in range(2)] + [wait_fixed(5) for i in range(8)]))
    def call(self, persuader_recent_history) -> ModeratorResponse:
        self.persuader_recent_history_last = persuader_recent_history[-2]


        history = ', '.join(str(t) for t in [tuple(dictionary.items()) for dictionary in persuader_recent_history[-6:]])

        for i in range(len(self.system_instruction)):
            message = self.model_backbone.run(temperature=0.5, messages=self._generate_prompt(i, history))
            if message == None:
                return None
            if i == 0:
                self.keep_talking = re.search(r"(?i)<KEEP-TALKING>", str(message))
                self.terminate = re.search(r"(?i)<TERMINATE>", str(message))
            elif i == 1:
                self.signal_check = re.search(r"(?i)True", str(message))
            elif i == 2:
                self.topic_check = re.search(r"(?i)<ON-TOPIC>", str(message))

        return self._generate_response()

    def _generate_prompt(self, i: int, history: str) -> list:
        prompt = [{
            "role": "system",
            "content": str(self.system_instruction[i])
        }, {
            "role": "user",
            "content": 'This is the history:{}'.format(history)
        }]

        if i == 1:

            prompt[1]['content'] = 'This is the message to check:{}'.format(self.persuader_recent_history_last)
        return prompt

    def _generate_response(self) -> ModeratorResponse:
        if self.signal_check:
            return ModeratorResponse(signal=SignalType.TERMINATE, terminate=True,
                                     info=ModeratorInfo.DEBATER_CONVINCED,
                                     result=True)
        else:
            self.not_convinced_counter += 1

        if self.not_convinced_counter > 10:
            return ModeratorResponse(signal=SignalType.TERMINATE, terminate=True,
                                     info=ModeratorInfo.DEBATER_NOT_CONVINCED,
                                     result=False)
        if self.terminate:
            return ModeratorResponse(signal=SignalType.TERMINATE, terminate=True, info=ModeratorInfo.GREETING,
                                     result=False)
        else:
            return ModeratorResponse(signal=SignalType.KEEP_TALKING, terminate=False, info=ModeratorInfo.NO_Action,
                                     result=False)
        if self.topic_check:
            return ModeratorResponse(signal=ModeratorInfo.DEBATE_ON_TOPIC_TOPIC, terminate=False, info=ModeratorInfo.DEBATE_ON_TOPIC,
                                     result=False)
        else:
            return ModeratorResponse(signal=SignalType.TERMINATE, terminate=True, info=ModeratorInfo.DEBATE_OFF_TOPIC,
                                     result=False)





    def helper_feedback(self):
        pass

    @property
    def last_response(self):
        pass

    @property
    def history(self):
        pass
