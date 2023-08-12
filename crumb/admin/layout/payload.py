from dataclasses import dataclass, field
from typing import Any, Protocol, TYPE_CHECKING, Optional, Callable, Coroutine

if TYPE_CHECKING:
    from .modal_box import ModalBox


@dataclass
class PayloadInfo:
    entity: str
    method: str
    query: dict[str, Any] = field(default_factory=dict)
    extra: Optional[dict[str, Any]] = None

