from copy import deepcopy
import ast
from typing import Optional, Any, Dict, List

from tenacity import retry, stop_after_attempt, wait_chain, wait_fixed

from utils import extract_prompt
from agents.debater import DebaterBase
from type import ModelType


class DebaterAgent(DebaterBase):
    def __init__(self,
                 model: Optional[ModelType] = None,
                 model_config: Optional[Any] = None,
                 prompt_instruction_path=None,
                 variables: Optional[Dict] = None,
                 memory_prompt_instruction_path=None,
                 evaluator_prompt_instruction_path: Optional[List] = None):
        self.evaluator_prompt_instruction_path = evaluator_prompt_instruction_path
        self.variables = variables
        system_instruction, ai_first_message = extract_prompt(prompt_instruction_path, self.variables)

        super().__init__(
            model,
            model_config,
            memory_prompt_instruction_path,
            debater_base="DebaterAgent"
        )

        # Add the system prompt to initial conversation
        self.memory.chat_memory.messages[0].system = system_instruction

        # The logger is used to have all the conversation, also, it holds the original system message
        self.memory.chat_memory.log.append(deepcopy(self.memory.chat_memory.messages[0]))

        # Always persuader starts the communication so we do not have assistant first message for Debater
        self.memory.limit_number = 4050

    @retry(stop=stop_after_attempt(5),
           wait=wait_chain(*[wait_fixed(2) for _ in range(2)] + [wait_fixed(5) for _ in range(16)]))
    def call(self, message):
        self.memory.add_user_message(message)
        message = self.model_backbone.run(**self.model_config.__dict__, messages=self.memory.prompt())
        self.memory.add_ai_message(message)
        return message

    @retry(stop=stop_after_attempt(5),
           wait=wait_chain(*[wait_fixed(2) for _ in range(2)] + [wait_fixed(5) for _ in range(16)]))
    def evaluate(self):
        # The inputs array in memory is checked for the max length after the last iteration so we can use it
        overall_conversation = self.memory.chat_memory.messages[0].inputs
        modified_array = []

        for dictionary in overall_conversation:
            # Change user to persuader and assistant to debater to help model better proceed the conversions
            # We are passing the debater memory in which debater responses are saved as assistant.
            modified_dict = {("persuader" if key == 'user' else "customer"): value for key, value in dictionary.items()}
            modified_array.append(modified_dict)

        self.variables["<HISTORY>"] = str(modified_array)
        evaluation_results = []

        for i in range(len(self.evaluator_prompt_instruction_path)):
            sys_instr, user_msg = extract_prompt(self.evaluator_prompt_instruction_path[i], self.variables)

            # Add history in case there were a summarization
            evaluator_prompt = [
                {"role": "system", "content": str(sys_instr)},
                {"role": "user", "content": str(self.memory.chat_memory.messages[0].history) + str(user_msg)}
            ]

            while True:
                evaluation = self.model_backbone.run(**self.model_config.__dict__, messages=evaluator_prompt)
                try:
                    evaluation_dict = ast.literal_eval(evaluation)

                    if isinstance(evaluation_dict, dict):
                        for keys in evaluation_dict.keys():
                            evaluation_results.append(evaluation_dict[keys])
                        break  # Break the loop if the code succeeds without errors

                except (SyntaxError, ValueError):
                    pass  # Continue to the next iteration of the loop if an error occurs

        return {index + 1: value for index, value in enumerate(evaluation_results)}

    def helper_feedback(self):
        pass
