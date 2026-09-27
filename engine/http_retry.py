from __future__ import annotations
import time
from typing import Callable, TypeVar
import httpx

T=TypeVar("T")
RETRY_STATUS={429,500,502,503,504}

def with_http_retry(call: Callable[[],T], *, attempts: int=4, base_delay: float=0.5,
                    sleeper: Callable[[float],None]=time.sleep) -> T:
    if attempts < 1: raise ValueError("attempts must be >= 1")
    last: Exception | None=None
    for attempt in range(attempts):
        try:
            return call()
        except httpx.HTTPStatusError as exc:
            last=exc
            if exc.response.status_code not in RETRY_STATUS or attempt==attempts-1:
                raise
        except (httpx.TimeoutException,httpx.NetworkError) as exc:
            last=exc
            if attempt==attempts-1: raise
        sleeper(base_delay*(2**attempt))
    assert last is not None
    raise last
