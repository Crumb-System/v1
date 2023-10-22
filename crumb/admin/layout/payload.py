from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class PayloadInfo:
    entity: str
    method: str
    query: dict[str, Any] = field(default_factory=dict)
    extra: Optional[dict[str, Any]] = None

