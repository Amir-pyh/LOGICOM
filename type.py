from enum import Enum


class ModelType(Enum):
    GPT_4_COMPLETION = None
    GPT_3_5_TURBO_COMPLETION = "text-davinci-003"
    GPT_4_32k_COMPLETION = None
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    GPT_3_5_TURBO_0301 = "gpt-3.5-turbo-0301"
    GPT_3_5_TURBO_0613 = "gpt-3.5-turbo-0613"
    GPT_3_5_TURBO_16k = "gpt-3.5-turbo-16k"
    GPT_3_5_TURBO_16k_01613 = "gpt-3.5-turbo-16k-0613"
    GPT_4 = "gpt-4"
    GPT_4_0314 = "gpt-4-0314"
    GPT_4_0613 = "gpt-4-0613"
    GPT_4_32k = "gpt-4-32k"
    PaLM = "models/chat-bison-001"
    PaLM_TEXT_GENERATION = "models/chat-bison-001_TEXT"


class AgentType(Enum):
    DEBATER_AGENT = "debater_agent"
    PERSUADER_AGENT = "persuader_agent"
    MODERATOR_AGENT = "moderator_agent"
    FALLACY_HELPER_AGENT = "fallacy_helper_agent"


class SignalType(Enum):
    TERMINATE = "TERMINATE"
    KEEP_TALKING = "KEEP-TALKING"


class ModeratorInfo(Enum):
    DEBATE_OFF_TOPIC = "Debate is off the topic"
    DEBATE_ON_TOPIC = "Debate is on topic"
    DEBATER_CONVINCED = "Persuader successfully convinced the debater"
    DEBATER_NOT_CONVINCED = "Persuader could not convince the debater"
    GREETING = "Agents are in greeting loop"
    NO_Action = "No Action From Moderator"
    ATTACH_I_AM_NOT_CONVINCED_ON_CLAIM = "attach <I_AM_NOT_CONVINCED_ON_CLAIM>"
    ATTACH_I_AM_CONVINCED_ON_CLAIM = "attach <I_AM_NOT_CONVINCED_ON_CLAIM>"
    WRONG_SIGNAL = "Wrong signal"


class ArgumentHelperType(Enum):
    pass
