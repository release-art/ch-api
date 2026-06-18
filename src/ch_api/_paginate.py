"""The ``@paginated`` decorator and the task-local channel it feeds.

Internal; not part of the public API.
"""

import contextvars
import functools
import inspect
import typing

import pydantic

from .types.pagination.types import _PageState

_PaginatedFn = typing.TypeVar("_PaginatedFn", bound=typing.Callable[..., typing.Awaitable[typing.Any]])


#: Task-local channel from :func:`paginated` to the fetch helpers, carrying the
#: active call's endpoint name and arguments (its position fields are unset here;
#: the helpers add those when stamping the ``next_page`` token). Task-local so
#: concurrent paginated calls on one client don't clash. An empty ``endpoint``
#: means no paginated call is active.
_resume_ctx: contextvars.ContextVar[typing.Optional[_PageState]] = contextvars.ContextVar(
    "ch_api_resume_ctx", default=None
)


def current_resume_state() -> _PageState:
    """The active ``@paginated`` call's :class:`_PageState`, or an empty one."""
    return _resume_ctx.get() or _PageState()


def paginated(*, exclude: typing.Collection[str] = ("self",)) -> typing.Callable[[_PaginatedFn], _PaginatedFn]:
    """Decorate an async ``Client`` method that returns a ``MultipageList``.

    * Validates arguments via :func:`pydantic.validate_call` (schema from the
      method's annotations).
    * Publishes the endpoint name and arguments on :data:`_resume_ctx` so the
      fetch helpers can build a replayable ``next_page`` token.

    Args:
        exclude: Argument names left out of the resume token's ``params``
            (cursor position is tracked separately). Defaults to ``self``.
    """
    excluded = set(exclude)

    def decorate(func: _PaginatedFn) -> _PaginatedFn:
        endpoint = func.__name__
        sig = inspect.signature(func)
        validated = pydantic.validate_call(func)

        @functools.wraps(func)
        async def wrapper(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            params = {name: value for name, value in bound.arguments.items() if name not in excluded}
            ctx_token = _resume_ctx.set(_PageState(endpoint=endpoint, params=params))
            try:
                result = await validated(*args, **kwargs)
            finally:
                _resume_ctx.reset(ctx_token)
            return result

        #: Marks the method as a resumable paginated endpoint. ``Client.fetch_next_page``
        #: only re-dispatches to methods carrying this flag, so the allowlist can never
        #: drift out of sync with the set of ``@paginated`` methods.
        wrapper._ch_paginated = True  # type: ignore[attr-defined]
        return typing.cast(_PaginatedFn, wrapper)

    return decorate
