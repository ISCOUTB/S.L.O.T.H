from typing import Generic, TypedDict, TypeVar

T = TypeVar("T")


class Paginated(TypedDict, Generic[T]):
    """
    Base model for paginated responses.

    Attributes:
        total (int): The total number of items available.
        page (int): The current page number.
        limit (int): The number of items per page.
        total_pages (int): The total number of pages available.
        has_next (bool): Indicates if there is a next page.
        has_prev (bool): Indicates if there is a previous page.
        items (list[T]): The list of items on the current page.
    """

    total: int
    page: int
    limit: int
    total_pages: int
    has_next: bool
    has_prev: bool
    items: list[T]
