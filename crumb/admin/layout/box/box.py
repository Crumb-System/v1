from typing import Protocol, Callable, Coroutine, TYPE_CHECKING

if TYPE_CHECKING:
    from crumb.admin.layout import PayloadInfo, ModalBox


class Box(Protocol):
    on_close: Callable[[], Coroutine[..., ..., None]]

    async def close(self):
        raise NotImplementedError

    async def add_modal(self, info: "PayloadInfo") -> "ModalBox":
        raise NotImplementedError

    def change_title(self, title: str):
        raise NotImplementedError

    @staticmethod
    def filter_payload_query(info: "PayloadInfo"):
        """убирает из query ключи, которые предназначены для Box"""
        return {k: v for k, v in info.query.items() if not k.startswith('BOX_')}
