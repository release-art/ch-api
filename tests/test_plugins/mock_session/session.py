import base64
import enum
import gzip
import json
import pathlib
import typing

import httpx

from . import cache_filename


@enum.unique
class CacheMode(enum.StrEnum):
    READ = "readonly"
    WRITE = "writeonly"
    FETCH_MISSING = "fetch_missing"


class CachingSession(httpx.AsyncClient):
    """A test-only session that caches responses to disk for reuse."""

    cache_dir: pathlib.Path
    cache_mode: CacheMode

    def __init__(
        self,
        headers: dict,
        cache_dir: pathlib.Path,
        cache_mode: typing.Literal["readonly", "writeonly", "fetch_missing"] = "readonly",
    ) -> None:
        super().__init__(headers=headers)
        self.cache_dir = pathlib.Path(cache_dir)
        self.cache_mode = CacheMode(cache_mode)

    def _get_cache_filename(self, request: httpx.Request) -> pathlib.Path:
        """Generate a cache filename based on the request parameters.

        Parameters
        ----------
        url : str
            The request URL.
        **kwargs : Any
            Additional request parameters.

        Returns
        -------
        pathlib.Path
            Path to the cache file.
        """
        # Create a unique identifier from URL and request parameters
        # This must match the logic in CachingFinancialServicesRegisterApiSession
        return self.cache_dir / cache_filename.make(request)

    async def _read_response_from_cache(self, cache_file: pathlib.Path) -> httpx.Response:
        """Read a cached response from disk.

        Parameters
        ----------
        cache_file : pathlib.Path
            Path to the cache file.

        Returns
        -------
        httpx.Response
            The cached HTTP response.
        """
        with cache_file.open("r") as f:
            cache_data = json.load(f)

        # Create a mock HTTP response
        # We need to construct the response in a way that httpx.Response accepts
        request = httpx.Request(
            "GET",
            cache_data["url"],
            params=cache_data["request"].get("params"),
        )

        if (binary_content := cache_data["content"].get("content", None)) is not None:
            content_payload = base64.b64decode(binary_content)
        elif json_content := cache_data["content"].get("json"):
            content_payload = json.dumps(json_content).encode("utf-8")
        else:
            raise NotImplementedError("Only JSON content is supported in the mock session.")
        response = httpx.Response(
            status_code=cache_data["status_code"],
            headers=cache_data["headers"] | {"content-encoding": "gzip"},
            content=gzip.compress(content_payload),
            request=request,
        )
        return response

    async def _make_and_save_request(
        self,
        cache_file: pathlib.Path,
        request: httpx.Request,
    ) -> httpx.Response:
        """Make an HTTP request and save the response to cache.

        Parameters
        ----------
        request: httpx.Request
            The HTTP request to be made.

        Returns
        -------
        httpx.Response
            The HTTP response.
        """
        if not cache_file.parent.exists():
            cache_file.parent.mkdir(parents=True, exist_ok=True)

        response = await super().send(request)
        if response.content == b"":
            content_dict = {
                "content": "",
            }
        else:
            content_dict = {
                # Assume JSON content for simplicity
                "json": response.json(),
            }
        cache_data = {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "content": content_dict,
            "url": str(response.url),
            "request": {
                "url": str(request.url),
                "params": request.extensions.get("params"),
                "headers": dict(self.headers)
                | {
                    # Mask private headers
                    "authorization": "Basic aGVsbG86d29ybGQ=",
                },
            },
        }

        with cache_file.open("w") as f:
            json.dump(cache_data, f, indent=2, sort_keys=True)
        return response

    async def send(self, request: httpx.Request) -> httpx.Response:
        cache_file = self._get_cache_filename(request)

        if self.cache_mode == CacheMode.READ:
            response = await self._read_response_from_cache(cache_file)
        elif self.cache_mode == CacheMode.WRITE:
            response = await self._make_and_save_request(cache_file, request)
        elif self.cache_mode == CacheMode.FETCH_MISSING:
            if cache_file.exists():
                response = await self._read_response_from_cache(cache_file)
            else:
                response = await self._make_and_save_request(cache_file, request)
        else:
            raise NotImplementedError(f"Unexpected cache mode for reading: {self.cache_mode}")

        return response
