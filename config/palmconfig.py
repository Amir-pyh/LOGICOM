from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=False)
class PaLMConfig:
    temperature: Optional[float] = None
    candidate_count: Optional[int] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None
