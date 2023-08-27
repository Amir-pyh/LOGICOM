from dataclasses import dataclass, field
from typing import Dict, Optional, Sequence, Union


@dataclass(frozen=False)
class ChatGPTConfig:
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    n: int = 1
    #best_of: int = 2
    stream: bool = False
    stop: Optional[Union[str, Sequence[str]]] = None
    max_tokens: Optional[int] = None
    presence_penalty: Optional[float] = None
    frequency_penalty: Optional[float] = None
    logit_bias: Dict = field(default_factory=dict)
    user: str = ""

