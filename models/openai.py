import sys
import tiktoken
import openai
import google.generativeai as palm
from google.generativeai.types import safety_types
from models.base import ModelBackbone
from type import ModelType
from typing import Any, Dict

enc = tiktoken.encoding_for_model("gpt-4")


class PaLMModelCompletion(ModelBackbone):
    def __init__(self, model_type: ModelType) -> None:
        super().__init__()
        self.model_type = model_type
        self.token_counter = 0

    def run(self, *args, **kwargs) -> Dict[str, Any]:
        excluded_keyword = 'messages'
        filtered_kwargs = {key: value for key, value in kwargs.items() if key != excluded_keyword}

        if 'messages' in kwargs:
            context = kwargs['messages'][0]
            messages = kwargs['messages']
            messages_modified = [
                {("author" if key == "role" else key): ("1" if key == "role" and value == "assistant" else "0" if key == "role" and value == "user" else value)
                 for key, value in dictionary.items()} for dictionary in messages[1:]]
            self.token_counter += len(enc.encode(str(messages)))

        safety_settings = [
            {"category": category, "threshold": safety_types.HarmBlockThreshold.BLOCK_NONE}
            for category in [
                safety_types.HarmCategory.HARM_CATEGORY_DEROGATORY,
                safety_types.HarmCategory.HARM_CATEGORY_VIOLENCE,
                safety_types.HarmCategory.HARM_CATEGORY_SEXUAL,
                safety_types.HarmCategory.HARM_CATEGORY_UNSPECIFIED,
                safety_types.HarmCategory.HARM_CATEGORY_TOXICITY,
                safety_types.HarmCategory.HARM_CATEGORY_DANGEROUS,
                safety_types.HarmCategory.HARM_CATEGORY_MEDICAL
            ]
        ]

        response = palm.generate_text(
            **filtered_kwargs,
            safety_settings=safety_settings,
            prompt="context:" + str(context['content']) + str(messages_modified)
        )

        return response.result

    @property
    def token_used(self):
        return self.token_counter


class PaLMModelChatCompletion(ModelBackbone):
    def __init__(self, model_type: ModelType) -> None:
        super().__init__()
        self.model_type = model_type
        self.token_counter = 0

    def run(self, *args, **kwargs) -> Dict[str, Any]:
        excluded_keyword = 'messages'
        filtered_kwargs = {key: value for key, value in kwargs.items() if key != excluded_keyword}

        if 'messages' in kwargs:
            context = kwargs['messages'][0]
            messages = kwargs['messages']
            messages_modified = [
                {("author" if key == "role" else key): ("1" if key == "role" and value == "assistant" else "0" if key == "role" and value == "user" else value)
                 for key, value in dictionary.items()} for dictionary in messages[1:]]
            self.token_counter += len(enc.encode(str(messages)))

        response = palm.chat(**filtered_kwargs, context=context['content'], messages=messages_modified)
        return response.last

    @property
    def token_used(self):
        return self.token_counter


class OpenAIModelChatCompletion(ModelBackbone):
    def __init__(self, model_type: ModelType) -> None:
        super().__init__()
        self.model_type = model_type
        self.token_counter = 0

    def run(self, *args, **kwargs) -> Dict[str, Any]:
        if 'messages' in kwargs:
            messages = kwargs['messages']
            self.token_counter += len(enc.encode(str(messages)))

        response = openai.ChatCompletion.create(*args, **kwargs, model=self.model_type.value)
        if not isinstance(response, Dict):
            raise RuntimeError("Unexpected return from OpenAI API")

        return response['choices'][0]['message']['content']

    @property
    def token_used(self):
        return self.token_counter


class OpenAIModelCompletion(ModelBackbone):
    def __init__(self, model_type: ModelType) -> None:
        super().__init__()
        self.model_type = model_type
        self.token_counter = 0

    def run(self, *args, **kwargs) -> Dict[str, Any]:
        if 'messages' in kwargs:
            messages = kwargs['messages']
            self.token_counter += len(enc.encode(str(messages)))

        response = openai.Completion.create(*args, **kwargs, model=self.model_type.value)
        if not isinstance(response, Dict):
            raise RuntimeError("Unexpected return from OpenAI API")

        return response

    @property
    def token_used(self):
        return self.token_counter


class ModelFactory:
    @staticmethod
    def create(model_type: ModelType) -> ModelBackbone:
        default_model_type = ModelType.GPT_3_5_TURBO

        model_class_map = {
            ModelType.GPT_3_5_TURBO: OpenAIModelChatCompletion,
            ModelType.GPT_3_5_TURBO_0301: OpenAIModelChatCompletion,
            ModelType.GPT_3_5_TURBO_0613: OpenAIModelChatCompletion,
            ModelType.GPT_3_5_TURBO_16k: OpenAIModelChatCompletion,
            ModelType.GPT_3_5_TURBO_16k_01613: OpenAIModelChatCompletion,
            ModelType.GPT_4: OpenAIModelChatCompletion,
            ModelType.GPT_4_32k: OpenAIModelChatCompletion,
            ModelType.GPT_4_0613: OpenAIModelChatCompletion,
            ModelType.GPT_4_0314: OpenAIModelChatCompletion,
            ModelType.GPT_3_5_TURBO_COMPLETION: OpenAIModelCompletion,
            ModelType.GPT_4_COMPLETION: OpenAIModelCompletion,
            ModelType.GPT_4_32k_COMPLETION: OpenAIModelCompletion,
            ModelType.PaLM: PaLMModelChatCompletion,
            ModelType.PaLM_TEXT_GENERATION: PaLMModelCompletion
        }

        model_class = model_class_map.get(model_type, OpenAIModelChatCompletion)
        inst = model_class(model_type or default_model_type)
        return inst
