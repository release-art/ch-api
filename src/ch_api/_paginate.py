"""Internal runtime for paginated ``Client`` endpoints.

Houses the :func:`paginated` decorator and the task-local channel it uses to
hand ``(endpoint_name, call_params)`` to the fetch helpers in :mod:`ch_api.api`,
which stamp them into self-contained, replayable ``next_page`` tokens. Kept out
of ``api.py`` to keep that module focused on the endpoint surface.

Not part of the public API.
"""

import contextvars
import functools
import inspect
import typing

import pydantic

_PaginatedFn = typing.TypeVar("_PaginatedFn", bound=typing.Callable[..., typing.Awaitable[typing.Any]])

#: Task-local channel carrying ``(endpoint_name, call_params)`` from the
#: :func:`paginated` decorator down to the fetch helpers, which stamp them into
#: the outgoing ``next_page`` token. Task-local (not instance state) so concurrent
#: paginated calls on the same client never clash.
_resume_ctx: contextvars.ContextVar[typing.Optional[typing.Tuple[str, dict]]] = contextvars.ContextVar(
    "ch_api_resume_ctx", default=None
)


def current_resume_identity() -> typing.Tuple[str, dict]:
    """Return the ``(endpoint, params)`` published by the active ``@paginated`` call.

    Returns ``("", {})`` when called outside a paginated method (e.g. a fetch
    helper invoked directly in a test) — in that case the produced token is
    position-only and not replayable via :meth:`ch_api.api.Client.fetch_next_page`.
    """
    return _resume_ctx.get() or ("", {})


def paginated(
    *, exclude: typing.Collection[str] = ("self", "next_page")
) -> typing.Callable[[_PaginatedFn], _PaginatedFn]:
    """Decorator for async ``Client`` methods that return a ``MultipageList``.

    Folds three concerns together so endpoint bodies stay minimal:

    * Applies :func:`pydantic.validate_call` — its schema is derived from the
      method's own annotations, so no separate argument spec is needed.
    * Captures the endpoint name (``func.__name__``) and the call's arguments and
      publishes them on a task-local context var that the fetch helpers read to
      build a self-contained, replayable ``next_page`` token (see
      :meth:`ch_api.api.Client.fetch_next_page`).
    * Binds the originating client to the returned list so
      :meth:`~ch_api.types.pagination.types.MultipageList.get_next` works.

    Args:
        exclude: Argument names omitted from the resume token's ``params``.
            Defaults to ``self`` and ``next_page`` (cursor position is tracked
            separately by the fetch helpers).
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
            ctx_token = _resume_ctx.set((endpoint, params))
            try:
                result = await validated(*args, **kwargs)
            finally:
                _resume_ctx.reset(ctx_token)
            result._client = args[0]  # bind the Client (self) for get_next()
            return result

        return typing.cast(_PaginatedFn, wrapper)

    return decorate
