from typing import Self, Optional, Callable, Coroutine

from flet import Row, Container, Text, Icon, icons, MainAxisAlignment


class Paginator(Row):

    def __init__(
            self,
            on_current_change: Callable[[], Coroutine[..., ..., None]],
            per_page: int,
            per_page_variants: tuple[int, ...],
            count: int = 7,
    ):
        Row.__init__(self, alignment=MainAxisAlignment.END)
        assert per_page in per_page_variants, f'{per_page} not in {per_page_variants}'
        self.per_page = per_page
        self.per_page_variants = per_page_variants
        self.count = count
        self.total = 1
        self.current = 1
        self._btn_prev = PageBtn(paginator=self).prev()
        self._btn_next = PageBtn(paginator=self).next()
        self.on_current_change = on_current_change

        self._per_page_control = Row()
        self._pages_control = Row()
        self.controls = [self._per_page_control, self._pages_control]

    @property
    def skip(self) -> int:
        return (self.current - 1) * self.limit

    @property
    def limit(self) -> int:
        return self.per_page

    async def set_current(self, num: int):
        self.current = num
        await self.on_current_change()

    def build_pages(self):
        pages = []
        for num in self.calc():
            btn = PageBtn(paginator=self)
            btn.ellipsis() if num == '...' else btn.number(num, current=self.current == num)
            pages.append(btn)
        self._btn_prev.disable() if self.current == 1 else self._btn_prev.enable()
        self._btn_next.disable() if self.current == self.total else self._btn_next.enable()
        self._pages_control.controls = [self._btn_prev, *pages, self._btn_next]

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


class PageBtn(Container):
    def __init__(self, paginator: Paginator):
        Container.__init__(self, padding=5, border_radius=5)
        self.paginator = paginator
        self.type = None
        self.page_number: Optional[int] = None

    def ellipsis(self) -> Self:
        assert self.type is None
        self.type = 'ellipsis'
        self.content = Text('...')
        return self

    def number(self, num: int, current: bool) -> Self:
        assert self.type is None
        self.type = 'numeric'
        self.page_number = num
        if current:
            self.content = Text(str(self.page_number), color='white')
            self.bgcolor = 'primary'
        else:
            self.content = Text(str(self.page_number), color='primary')
            self.on_click = self.on_click_num
        return self

    def next(self) -> Self:
        assert self.type is None
        self.type = 'next'
        self.content = Icon(icons.CHEVRON_RIGHT, color='primary')
        self.on_click = self.on_click_next
        return self

    def prev(self) -> Self:
        assert self.type is None
        self.type = 'prev'
        self.content = Icon(icons.CHEVRON_LEFT, color='primary')
        self.on_click = self.on_click_prev
        return self

    def disable(self) -> Self:
        assert self.type in ('next', 'prev')
        if not self.disabled:
            self.disabled = True
            self.content.color = 'grey'
        return self

    def enable(self):
        assert self.type in ('next', 'prev')
        if self.disabled:
            self.disabled = False
            self.content.color = 'primary'
        return self

    async def on_click_prev(self, e=None):
        if self.paginator.current > 1:
            await self.paginator.set_current(self.paginator.current - 1)

    async def on_click_next(self, e=None):
        if self.paginator.current < self.paginator.total:
            await self.paginator.set_current(self.paginator.current + 1)

    async def on_click_num(self, e=None):
        await self.paginator.set_current(self.page_number)
