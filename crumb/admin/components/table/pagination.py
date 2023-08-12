from typing import TYPE_CHECKING

from flet import Row, ContainerTapEvent, Container, Text, Icon, MainAxisAlignment, icons

if TYPE_CHECKING:
    from crumb.admin import Datagrid


class Pagination(Row):

    """
    Обновление записей таблицы происходит при
     - Изменении current
     - Изменении per_page (current так же становится 1)

    """

    _total: int = 1
    _current: int = 1

    def __init__(
            self,
            datagrid: "Datagrid",
            *,
            count: int = 7,
            per_page: int = 25,
    ):
        super().__init__()
        self.datagrid = datagrid
        self.count = count
        self.per_page = per_page
        self.alignment = MainAxisAlignment.END

    @property
    def total(self) -> int:
        return self._total

    @total.setter
    def total(self, v: int):
        self._total = v
        self.btn_next.disabled = self.current == self.total

    @property
    def current(self) -> int:
        return self._current

    @current.setter
    def current(self, v: int):
        assert 1 <= v <= self.total
        self._current = v
        self.btn_previous.disabled = self.current == 1
        self.btn_next.disabled = self.current == self.total

    @property
    def count(self) -> int:
        return self._count

    @count.setter
    def count(self, v: int):
        assert v > 0 and v % 2 == 1
        self._count = v

    @property
    def per_page(self) -> int:
        return self._per_page

    @per_page.setter
    def per_page(self, v: int):
        assert v > 0
        self._per_page = v
        self.current = 1

    @property
    def skip(self) -> int:
        return (self.current - 1) * self.limit

    @property
    def limit(self) -> int:
        return self.per_page

    def set_current_on_click(self, number: int):
        async def handler(e: ContainerTapEvent):
            await self.set_current(number)

        return handler

    async def set_current(self, number: int):
        self.current = number
        await self.datagrid.update_datagrid()

    async def set_per_page(self, per_page: int):
        self.per_page = per_page
        await self.datagrid.update_datagrid()

    @property
    def btn_previous(self) -> Container:
        if not hasattr(self, '_btn_previous'):
            async def set_previous_page(e: ContainerTapEvent):
                await self.set_current(self.current - 1)

            btn = Container(
                content=Icon(icons.CHEVRON_LEFT),
                on_click=set_previous_page
            )
            setattr(self, '_btn_previous', btn)
        return getattr(self, '_btn_previous')

    @property
    def btn_next(self) -> Container:
        if not hasattr(self, '_btn_next'):
            async def set_next_page(e: ContainerTapEvent):
                await self.set_current(self.current + 1)

            btn = Container(
                content=Icon(icons.CHEVRON_RIGHT),
                on_click=set_next_page
            )
            setattr(self, '_btn_next', btn)
        return getattr(self, '_btn_next')

    def rebuild(self):
        self.controls = [self.btn_previous]
        for cell in self.calc():
            el = Container(Text(cell))
            if cell != '...':
                number = int(cell)
                if number == self.current:
                    el.bgcolor = 'blue'
                    el.border_radius = 5
                else:
                    el.on_click = self.set_current_on_click(number)
            self.controls.append(el)
        self.controls.append(self.btn_next)

    def calc(self):
        result = []
        # если всего страниц, например, 5, а элементов максимум 7
        if self.total <= self.count:
            for i in range(1, self.total + 1):
                result.append(i)
            return result

        # Остальное с точками
        first_page = 1
        confirmed_pages_count = 3
        deducted_count = self.count - confirmed_pages_count
        side_length = deducted_count // 2

        # когда элипсис 1 и по середине
        if self.current - first_page < side_length or self.total - self.current < side_length:
            for i in range(1, side_length + first_page + 1):
                result.append(i)
            result.append('...')
            for i in range(self.total - side_length, self.total + 1):
                result.append(i)

        # когда элипсиса 2
        elif self.current - first_page >= deducted_count and self.total - self.current >= deducted_count:
            deducted_side_length = side_length - 1
            result.append(1)
            result.append('...')

            for i in range(self.current - deducted_side_length, self.current + deducted_side_length + 1):
                result.append(i)

            result.append('...')
            result.append(self.total)

        # когда элипсис один, но не по середине
        else:
            is_near_first_page = self.current - first_page < self.total - self.current
            remaining_length = self.count

            if is_near_first_page:
                for i in range(1, self.current + 2):
                    result.append(i)
                    remaining_length -= 1
                result.append('...')
                remaining_length -= 1
                for i in range(self.total - (remaining_length - 1), self.total + 1):
                    result.append(i)
            else:
                for i in range(self.total, self.current - 2, -1):
                    result.insert(0, i)
                    remaining_length -= 1
                result.insert(0, '...')
                remaining_length -= 1
                for i in range(remaining_length, 0, -1):
                    result.insert(0, i)

        return result
