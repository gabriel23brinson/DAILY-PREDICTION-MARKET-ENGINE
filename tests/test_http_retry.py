import httpx
import pytest
from engine.http_retry import with_http_retry

def status_error(code: int) -> httpx.HTTPStatusError:
    request=httpx.Request("GET","https://example.test")
    response=httpx.Response(code,request=request)
    return httpx.HTTPStatusError("test",request=request,response=response)

def test_transient_status_retries_then_succeeds():
    calls=[]
    sleeps=[]
    def call():
        calls.append(1)
        if len(calls)<3: raise status_error(429)
        return "ok"
    assert with_http_retry(call,attempts=4,base_delay=.1,sleeper=sleeps.append)=="ok"
    assert len(calls)==3
    assert sleeps==[.1,.2]

def test_permanent_client_error_does_not_retry():
    calls=[]
    def call():
        calls.append(1)
        raise status_error(400)
    with pytest.raises(httpx.HTTPStatusError):
        with_http_retry(call,attempts=4,sleeper=lambda _:None)
    assert len(calls)==1

def test_transient_failure_is_bounded():
    calls=[]
    def call():
        calls.append(1)
        raise httpx.TimeoutException("timeout")
    with pytest.raises(httpx.TimeoutException):
        with_http_retry(call,attempts=3,base_delay=0,sleeper=lambda _:None)
    assert len(calls)==3
