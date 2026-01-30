"""Customised pagination types for public data endpoints."""

import typing

import ch_api.types.base as base
import ch_api.types.pagination as main_pagination

ITEM_T = typing.TypeVar("ITEM_T", bound=base.BaseModel)
CONTAINER_T = typing.TypeVar("CONTAINER_T", bound=base.BaseModel)


ConverRvT = typing.Tuple[
    typing.Optional[main_pagination.types.PaginatedResultInfo],
    typing.Optional[CONTAINER_T],
]


class _PaginatedEntityInitCls(typing.Generic[CONTAINER_T, ITEM_T]):
    """A helper class to allow async initialization in PaginatedEntity."""

    fetch_page_fn: typing.Callable[[main_pagination.types.FetchPageCallArg], typing.Awaitable[ConverRvT[CONTAINER_T]]]
    convert_item_fn: typing.Callable[[CONTAINER_T], typing.Sequence[ITEM_T]]
    convert_to_my_args: typing.Callable[[CONTAINER_T], dict]
    last_fetched_container: typing.Optional[CONTAINER_T | typing.Literal["__uninitialised__"]]

    def __init__(
        self,
        fetch_page_fn: typing.Callable[
            [main_pagination.types.FetchPageCallArg], typing.Awaitable[ConverRvT[CONTAINER_T]]
        ],
        convert_item_fn: typing.Callable[[CONTAINER_T], typing.Sequence[ITEM_T]],
        convert_to_my_args: typing.Optional[typing.Callable[[CONTAINER_T], dict]],
    ) -> None:
        self.last_fetched_container = "__uninitialised__"
        self.convert_item_fn = convert_item_fn
        self.fetch_page_fn = fetch_page_fn
        if convert_to_my_args is None:

            def default_convert_to_my_args(container: CONTAINER_T | None) -> dict:
                if container is None:
                    out = {}
                else:
                    out = container.model_dump(mode="python")
                return out

            self.convert_to_my_args = default_convert_to_my_args
        else:
            self.convert_to_my_args = convert_to_my_args

    async def multipage_list_cb(
        self, target: main_pagination.types.FetchPageCallArg
    ) -> main_pagination.types.FetchPageRvT[ITEM_T]:
        """Callback to fetch a page and convert items."""
        (pagination_info, container_val) = await self.fetch_page_fn(target)
        if container_val is None:
            rv_items = ()
        else:
            assert isinstance(container_val, base.BaseModel), type(container_val)
            rv_items = self.convert_item_fn(container_val)
        self.last_fetched_container = container_val
        return (pagination_info, rv_items)

    async def async_init(self, my_list: main_pagination.paginated_list.MultipageList[ITEM_T]) -> dict:
        """Perform any async initialization if needed."""
        await my_list._async_init()
        assert self.last_fetched_container != "__uninitialised__", "No data fetched during initialization"
        return self.convert_to_my_args(
            self.last_fetched_container  # type: ignore[arg-type]
        )


class PaginatedEntity(base.BaseModel, typing.Generic[CONTAINER_T, ITEM_T]):
    """A paginated list of entities with customised links section."""

    items: main_pagination.paginated_list.MultipageList[ITEM_T]

    @classmethod
    async def from_api_paginated_list(
        cls,
        fetch_page_fn: typing.Callable[
            [main_pagination.types.FetchPageCallArg], typing.Awaitable[ConverRvT[CONTAINER_T]]
        ],
        convert_item_fn: typing.Callable[[CONTAINER_T], typing.Sequence[ITEM_T]],
        convert_to_my_args: typing.Optional[typing.Callable[[CONTAINER_T], dict]] = None,
    ) -> "PaginatedEntity":
        """Create a PaginatedEntity instance from a paginated list.

        Parameters
        ----------
            fetch_page_fn: pagination.types.FetchPageCallableT[public_data.officer_appointments.AppointmentList]
                The function to fetch pages.

        Returns
        -------
            PaginatedEntity[T]
                The created PaginatedEntity instance.
        """
        converter = _PaginatedEntityInitCls(
            fetch_page_fn=fetch_page_fn,
            convert_item_fn=convert_item_fn,
            convert_to_my_args=convert_to_my_args,
        )
        my_list = main_pagination.paginated_list.MultipageList[ITEM_T](fetch_page=converter.multipage_list_cb)
        my_args = await converter.async_init(my_list)
        return cls.model_validate(my_args | {"items": my_list})  # type: ignore[return-value]
