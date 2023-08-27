import time
import ast
from copy import deepcopy
from typing import Optional, Any, Dict

from tenacity import wait_chain, wait_fixed, stop_after_attempt, retry

from models.base import ModelBackbone
from models.openai import ModelFactory
from utils import extract_prompt
from agents.debater import DebaterBase
from type import ModelType


class PersuaderAgent(DebaterBase):
    def __init__(self,
                 model: Optional[ModelType] = None,
                 model_helper: Optional[ModelType] = None,
                 model_config: Optional[Any] = None,
                 prompt_instruction_path=None,
                 helper_prompt_instruction_path=None,
                 variables: Optional[Dict] = None,
                 memory_prompt_instruction_path=None,
                 helper_feedback: bool = False):

        self.variables = variables
        system_instruction, ai_first_message = extract_prompt(prompt_instruction_path, self.variables)
        self.helper_prompt_instruction_path = helper_prompt_instruction_path
        self.helper_feedback_switch = helper_feedback

        super().__init__(model, model_config, memory_prompt_instruction_path, debater_base="PersuaderAgent")
        self.model_backbone_helper: ModelBackbone = ModelFactory.create(model_type=model_helper)

        self.memory.chat_memory.messages[0].system = system_instruction
        self.memory.chat_memory.log.append(deepcopy(self.memory.chat_memory.messages[0]))
        self.memory.add_ai_message(ai_first_message)

    @retry(stop=stop_after_attempt(5),
           wait=wait_chain(*[wait_fixed(2)] * 2 + [wait_fixed(5)] * 16))
    def call(self, message):
        self.memory.add_user_message(message)
        message = self.model_backbone.run(**self.model_config.__dict__, messages=self.memory.prompt())

        if self.helper_feedback_switch:
            modified_array = [{("AI" if key == "user" else "human"): value for key, value in dictionary.items()} for
                              dictionary in self.memory.chat_memory.messages[0].inputs]

            self.variables["<ASSISTANT_RESPONSE>"] = str(message)
            self.variables["<HISTORY>"] = str(modified_array)

            system_instruction_helper, user_instruction_helper = extract_prompt(self.helper_prompt_instruction_path,
                                                                                self.variables)
            feedback, fallacy, feedback_dict, fallacious_argument = self.helper_feedback(system_instruction_helper,
                                                                                         user_instruction_helper)

            self.memory.add_ai_message(message=str(feedback), fallacy_type=feedback_dict)
            return feedback, fallacy, fallacious_argument

        else:
            self.memory.add_ai_message(str(message))
            return message, "No Fallacy"

    @retry(stop=stop_after_attempt(5),
           wait=wait_chain(*[wait_fixed(2)] * 2 + [wait_fixed(5)] * 16))
    def helper_feedback(self, system_instruction_helper, user_instruction_helper) -> str:
        helper_prompt = [
            {"role": "system", "content": str(system_instruction_helper)},
            {"role": "user", "content": str(user_instruction_helper)}
        ]

        while True:
            feedback = self.model_backbone_helper.run(messages=helper_prompt).replace('\n\n', '').replace('\n', '')

            try:
                feedback_dict = ast.literal_eval(feedback)
                keys_list = list(feedback_dict.keys())
                fallacy, fallacious, feedback = feedback_dict[keys_list[0]], feedback_dict[keys_list[1]], feedback_dict[
                    keys_list[2]]
                break

            except (SyntaxError, ValueError):
                print('in except ')
                self.model_config.temperature = 0.5
                helper_prompt = [
                    {"role": "system", "content": str(system_instruction_helper)},
                    {"role": "user",
                     "content": f"You have generated this before. Follow the syntax and give it back in a way that I can pass it to ast.literal_eval(), make sure not to change any content: {feedback}"}
                ]

            time.sleep(1)

        return str(feedback), fallacy, feedback_dict, fallacious
