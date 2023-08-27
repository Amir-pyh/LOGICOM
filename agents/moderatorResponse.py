from dataclasses import dataclass, field
from type import ModeratorInfo, SignalType

@dataclass(frozen=True)
class ModeratorResponse:
    signal: SignalType = None
    terminate: bool = False
    info: ModeratorInfo = None
    result: bool = False
